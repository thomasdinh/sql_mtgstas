from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
import mysql.connector
import pandas as pd
from datetime import datetime
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MTG Match Analysis API",
    description="REST API for analyzing Magic: The Gathering multiplayer matches",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

# Pydantic models
class PlayerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)

class Player(BaseModel):
    id: int
    name: str

class DeckCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    owner_id: int
    image_url: Optional[str] = None
    color: Optional[str] = Field(None, max_length=32)
    deck_url: Optional[str] = None

class Deck(BaseModel):
    id: int
    name: str
    owner_id: int
    owner_name: str
    image_url: Optional[str] = None
    color: Optional[str] = None
    deck_url: Optional[str] = None

class MatchCreate(BaseModel):
    deck_lists: List[int] = Field(..., min_items=2)
    match_result: List[int] = Field(..., min_items=2)
    group_id: int
    date: Optional[str] = None

class Match(BaseModel):
    id: int
    deck_lists: str
    date: str
    winner_deck_id: int
    group_id: int
    winner_deck_name: Optional[str] = None
    winner_player_name: Optional[str] = None
    group_name: Optional[str] = None

class DeckStats(BaseModel):
    deck_id: int
    wins: int
    losses: int
    total_games: int
    winrate: float
    recent_matches: List[Dict]

class MatchupData(BaseModel):
    opponent_deck_id: int
    opponent_deck_name: str
    opponent_player_name: str
    wins: int
    losses: int
    total_games: int
    winrate: float

class MetaData(BaseModel):
    deck_id: int
    deck_name: str
    deck_color: Optional[str]
    player_name: str
    total_matches: int
    wins: int
    winrate: float
    meta_share: float

class Playgroup(BaseModel):
    id: int
    name: str

class PlaygroupStats(BaseModel):
    group_id: int
    total_matches: int
    popular_decks: List[Dict]
    recent_activity: List[Dict]

class HealthCheck(BaseModel):
    status: str
    timestamp: str

# Database connection manager
class MTGDatabase:
    def __init__(self, config: Dict):
        self.config = config
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Tuple = None, fetch: bool = True):
        """Execute a database query"""
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return cursor.rowcount

# Initialize database
db = MTGDatabase(DB_CONFIG)

# Dependency to get database instance
def get_database():
    return db

# Utility functions
def flatten_single_tuple_list(tuple_list: List[Tuple]) -> List:
    """Convert list of single-item tuples to flat list"""
    return [item[0] for item in tuple_list]

def parse_match_result(result_str: str) -> List[int]:
    """Parse match result string to list of integers"""
    result_str = result_str.strip('[]')
    return [int(x.strip()) for x in result_str.split(',')]

# API Routes

@app.get("/api/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

# Player endpoints
@app.get("/api/players", response_model=List[Player])
async def get_players(db: MTGDatabase = Depends(get_database)):
    """Get all players"""
    try:
        query = "SELECT PlayerID, Name FROM Player"
        results = db.execute_query(query)
        return [Player(id=row[0], name=row[1]) for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/players", response_model=Player, status_code=201)
async def create_player(player: PlayerCreate, db: MTGDatabase = Depends(get_database)):
    """Create a new player"""
    try:
        # Get next player ID
        max_id_query = "SELECT COALESCE(MAX(PlayerID), 0) + 1 FROM Player"
        next_id = db.execute_query(max_id_query)[0][0]
        
        query = "INSERT INTO Player (PlayerID, Name) VALUES (%s, %s)"
        db.execute_query(query, (next_id, player.name), fetch=False)
        
        return Player(id=next_id, name=player.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/players/{player_id}", response_model=Player)
async def get_player(player_id: int, db: MTGDatabase = Depends(get_database)):
    """Get specific player"""
    try:
        query = "SELECT PlayerID, Name FROM Player WHERE PlayerID = %s"
        results = db.execute_query(query, (player_id,))
        if not results:
            raise HTTPException(status_code=404, detail="Player not found")
        
        return Player(id=results[0][0], name=results[0][1])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Deck endpoints
@app.get("/api/decks", response_model=List[Deck])
async def get_decks(
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    db: MTGDatabase = Depends(get_database)
):
    """Get all decks with optional filtering"""
    try:
        if owner_id:
            query = """
                SELECT d.DeckID, d.DeckName, d.DeckOwnerID, p.Name as OwnerName, 
                       d.DeckImgURL, d.DeckColor, d.DeckURL
                FROM Deck d
                JOIN Player p ON d.DeckOwnerID = p.PlayerID
                WHERE d.DeckOwnerID = %s
            """
            results = db.execute_query(query, (owner_id,))
        else:
            query = """
                SELECT d.DeckID, d.DeckName, d.DeckOwnerID, p.Name as OwnerName, 
                       d.DeckImgURL, d.DeckColor, d.DeckURL
                FROM Deck d
                JOIN Player p ON d.DeckOwnerID = p.PlayerID
            """
            results = db.execute_query(query)
        
        decks = []
        for row in results:
            decks.append(Deck(
                id=row[0],
                name=row[1],
                owner_id=row[2],
                owner_name=row[3],
                image_url=row[4],
                color=row[5],
                deck_url=row[6]
            ))
        
        return decks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/decks", response_model=Deck, status_code=201)
async def create_deck(deck: DeckCreate, db: MTGDatabase = Depends(get_database)):
    """Create a new deck"""
    try:
        # Get next deck ID
        max_id_query = "SELECT COALESCE(MAX(DeckID), 0) + 1 FROM Deck"
        next_id = db.execute_query(max_id_query)[0][0]
        
        query = """
            INSERT INTO Deck (DeckID, DeckName, DeckOwnerID, DeckImgURL, DeckColor, DeckURL)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            next_id,
            deck.name,
            deck.owner_id,
            deck.image_url,
            deck.color,
            deck.deck_url
        )
        
        db.execute_query(query, params, fetch=False)
        
        # Get owner name for response
        owner_query = "SELECT Name FROM Player WHERE PlayerID = %s"
        owner_result = db.execute_query(owner_query, (deck.owner_id,))
        owner_name = owner_result[0][0] if owner_result else "Unknown"
        
        return Deck(
            id=next_id,
            name=deck.name,
            owner_id=deck.owner_id,
            owner_name=owner_name,
            image_url=deck.image_url,
            color=deck.color,
            deck_url=deck.deck_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/decks/{deck_id}/stats", response_model=DeckStats)
async def get_deck_stats(deck_id: int, db: MTGDatabase = Depends(get_database)):
    """Get deck statistics"""
    try:
        # Get wins
        win_query = "SELECT COUNT(*) FROM mtgmatches WHERE winnerID = %s"
        wins = db.execute_query(win_query, (deck_id,))[0][0]
        
        # Get losses
        lose_query = "SELECT COUNT(*) FROM decklose WHERE deckid = %s"
        losses = db.execute_query(lose_query, (deck_id,))[0][0]
        
        # Calculate winrate
        total_games = wins + losses
        winrate = (wins * 100 / total_games) if total_games > 0 else 0
        
        # Get recent matches
        recent_matches_query = """
            SELECT m.MatchID, m.Date, m.WinnerID = %s as Won
            FROM mtgmatches m
            WHERE m.WinnerID = %s OR EXISTS (
                SELECT 1 FROM decklose dl WHERE dl.MatchID = m.MatchID AND dl.DeckID = %s
            )
            ORDER BY m.Date DESC
            LIMIT 10
        """
        recent_results = db.execute_query(recent_matches_query, (deck_id, deck_id, deck_id))
        
        recent_matches = []
        for row in recent_results:
            recent_matches.append({
                "match_id": row[0],
                "date": row[1],
                "won": bool(row[2])
            })
        
        return DeckStats(
            deck_id=deck_id,
            wins=wins,
            losses=losses,
            total_games=total_games,
            winrate=round(winrate, 2),
            recent_matches=recent_matches
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Match endpoints
@app.get("/api/matches", response_model=List[Match])
async def get_matches(
    group_id: Optional[int] = Query(None, description="Filter by group ID"),
    limit: int = Query(50, description="Limit number of results"),
    db: MTGDatabase = Depends(get_database)
):
    """Get all matches with optional filtering"""
    try:
        base_query = """
            SELECT m.MatchID, m.DeckLists, m.Date, m.WinnerID, m.groupID,
                   d.DeckName as WinnerDeckName, p.Name as WinnerPlayerName,
                   pg.GroupName
            FROM mtgmatches m
            LEFT JOIN Deck d ON m.WinnerID = d.DeckID
            LEFT JOIN Player p ON d.DeckOwnerID = p.PlayerID
            LEFT JOIN Playgroup pg ON m.groupID = pg.GroupID
        """
        
        if group_id:
            query = base_query + " WHERE m.groupID = %s ORDER BY m.Date DESC LIMIT %s"
            results = db.execute_query(query, (group_id, limit))
        else:
            query = base_query + " ORDER BY m.Date DESC LIMIT %s"
            results = db.execute_query(query, (limit,))
        
        matches = []
        for row in results:
            matches.append(Match(
                id=row[0],
                deck_lists=row[1],
                date=row[2],
                winner_deck_id=row[3],
                group_id=row[4],
                winner_deck_name=row[5],
                winner_player_name=row[6],
                group_name=row[7]
            ))
        
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/matches", response_model=Match, status_code=201)
async def create_match(match: MatchCreate, db: MTGDatabase = Depends(get_database)):
    """Create a new match"""
    try:
        # Validate input
        if len(match.deck_lists) != len(match.match_result):
            raise HTTPException(
                status_code=400, 
                detail="deck_lists and match_result must have the same length"
            )
        
        # Get next match ID
        max_id_query = "SELECT COALESCE(MAX(MatchID), 0) + 1 FROM mtgmatches"
        next_id = db.execute_query(max_id_query)[0][0]
        
        # Process match data
        date = match.date or datetime.now().strftime('%Y-%m-%d')
        
        # Determine winner (assuming first place in result list is winner)
        winner_position = match.match_result.index(1) if 1 in match.match_result else 0
        winner_deck_id = match.deck_lists[winner_position]
        
        # Insert match
        match_query = """
            INSERT INTO mtgmatches (MatchID, DeckLists, Date, WinnerID, groupID)
            VALUES (%s, %s, %s, %s, %s)
        """
        deck_lists_str = ','.join(map(str, match.deck_lists))
        db.execute_query(match_query, (next_id, deck_lists_str, date, winner_deck_id, match.group_id), fetch=False)
        
        # Insert win/loss records
        for i, deck_id in enumerate(match.deck_lists):
            result = match.match_result[i]
            if result == 1:  # Win
                win_query = """
                    INSERT INTO deckwin (MatchID, DeckID, OpponentDeckID, Result, Date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                opponents = [d for j, d in enumerate(match.deck_lists) if j != i]
                for opponent in opponents:
                    db.execute_query(win_query, (next_id, deck_id, opponent, result, date), fetch=False)
            else:  # Loss
                lose_query = """
                    INSERT INTO decklose (MatchID, DeckID, OpponentDeckID, Result, Date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute_query(lose_query, (next_id, deck_id, winner_deck_id, result, date), fetch=False)
        
        # Get additional info for response
        deck_query = "SELECT DeckName FROM Deck WHERE DeckID = %s"
        deck_result = db.execute_query(deck_query, (winner_deck_id,))
        winner_deck_name = deck_result[0][0] if deck_result else None
        
        group_query = "SELECT GroupName FROM Playgroup WHERE GroupID = %s"
        group_result = db.execute_query(group_query, (match.group_id,))
        group_name = group_result[0][0] if group_result else None
        
        return Match(
            id=next_id,
            deck_lists=deck_lists_str,
            date=date,
            winner_deck_id=winner_deck_id,
            group_id=match.group_id,
            winner_deck_name=winner_deck_name,
            group_name=group_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Playgroup endpoints
@app.get("/api/playgroups", response_model=List[Playgroup])
async def get_playgroups(db: MTGDatabase = Depends(get_database)):
    """Get all playgroups"""
    try:
        query = "SELECT GroupID, GroupName FROM Playgroup"
        results = db.execute_query(query)
        return [Playgroup(id=row[0], name=row[1]) for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/playgroups/{group_id}/stats", response_model=PlaygroupStats)
async def get_playgroup_stats(group_id: int, db: MTGDatabase = Depends(get_database)):
    """Get playgroup statistics"""
    try:
        # Total matches in group
        total_matches_query = "SELECT COUNT(*) FROM mtgmatches WHERE groupID = %s"
        total_matches = db.execute_query(total_matches_query, (group_id,))[0][0]
        
        # Most played decks in group
        deck_usage_query = """
            SELECT d.DeckID, d.DeckName, p.Name as PlayerName, COUNT(*) as GamesPlayed
            FROM mtgmatches m
            JOIN Deck d ON (m.WinnerID = d.DeckID OR EXISTS (
                SELECT 1 FROM decklose dl WHERE dl.MatchID = m.MatchID AND dl.DeckID = d.DeckID
            ))
            JOIN Player p ON d.DeckOwnerID = p.PlayerID
            WHERE m.groupID = %s
            GROUP BY d.DeckID, d.DeckName, p.Name
            ORDER BY GamesPlayed DESC
            LIMIT 10
        """
        deck_usage_results = db.execute_query(deck_usage_query, (group_id,))
        
        popular_decks = []
        for row in deck_usage_results:
            popular_decks.append({
                "deck_id": row[0],
                "deck_name": row[1],
                "player_name": row[2],
                "games_played": row[3]
            })
        
        # Recent activity
        recent_activity_query = """
            SELECT m.MatchID, m.Date, d.DeckName, p.Name
            FROM mtgmatches m
            JOIN Deck d ON m.WinnerID = d.DeckID
            JOIN Player p ON d.DeckOwnerID = p.PlayerID
            WHERE m.groupID = %s
            ORDER BY m.Date DESC
            LIMIT 5
        """
        recent_results = db.execute_query(recent_activity_query, (group_id,))
        
        recent_activity = []
        for row in recent_results:
            recent_activity.append({
                "match_id": row[0],
                "date": row[1],
                "winner_deck": row[2],
                "winner_player": row[3]
            })
        
        return PlaygroupStats(
            group_id=group_id,
            total_matches=total_matches,
            popular_decks=popular_decks,
            recent_activity=recent_activity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/api/analytics/deck-matchups", response_model=List[MatchupData])
async def get_deck_matchups(
    deck_id: int = Query(..., description="Deck ID to analyze matchups for"),
    db: MTGDatabase = Depends(get_database)
):
    """Get deck matchup data"""
    try:
        # Get matchup data
        matchup_query = """
            SELECT 
                d.DeckID,
                d.DeckName,
                p.Name as PlayerName,
                SUM(CASE WHEN dw.Result = 1 THEN 1 ELSE 0 END) as Wins,
                SUM(CASE WHEN dl.Result = 0 THEN 1 ELSE 0 END) as Losses
            FROM Deck d
            JOIN Player p ON d.DeckOwnerID = p.PlayerID
            LEFT JOIN deckwin dw ON d.DeckID = dw.OpponentDeckID AND dw.DeckID = %s
            LEFT JOIN decklose dl ON d.DeckID = dl.OpponentDeckID AND dl.DeckID = %s
            WHERE d.DeckID != %s
            GROUP BY d.DeckID, d.DeckName, p.Name
            HAVING (Wins + Losses) > 0
            ORDER BY (Wins + Losses) DESC
        """
        
        results = db.execute_query(matchup_query, (deck_id, deck_id, deck_id))
        
        matchups = []
        for row in results:
            total_games = row[3] + row[4]
            winrate = (row[3] * 100 / total_games) if total_games > 0 else 0
            matchups.append(MatchupData(
                opponent_deck_id=row[0],
                opponent_deck_name=row[1],
                opponent_player_name=row[2],
                wins=row[3],
                losses=row[4],
                total_games=total_games,
                winrate=round(winrate, 2)
            ))
        
        return matchups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/meta", response_model=List[MetaData])
async def get_meta_analysis(
    group_id: Optional[int] = Query(None, description="Filter by group ID"),
    db: MTGDatabase = Depends(get_database)
):
    """Get meta analysis data"""
    try:
        base_query = """
            SELECT 
                d.DeckID,
                d.DeckName,
                d.DeckColor,
                p.Name as PlayerName,
                COUNT(DISTINCT m.MatchID) as TotalMatches,
                SUM(CASE WHEN m.WinnerID = d.DeckID THEN 1 ELSE 0 END) as Wins
            FROM Deck d
            JOIN Player p ON d.DeckOwnerID = p.PlayerID
            JOIN mtgmatches m ON (m.WinnerID = d.DeckID OR EXISTS (
                SELECT 1 FROM decklose dl WHERE dl.MatchID = m.MatchID AND dl.DeckID = d.DeckID
            ))
        """
        
        if group_id:
            query = base_query + " WHERE m.groupID = %s GROUP BY d.DeckID ORDER BY TotalMatches DESC"
            results = db.execute_query(query, (group_id,))
        else:
            query = base_query + " GROUP BY d.DeckID ORDER BY TotalMatches DESC"
            results = db.execute_query(query)
        
        meta_data = []
        for row in results:
            total_matches = row[4]
            wins = row[5]
            winrate = (wins * 100 / total_matches) if total_matches > 0 else 0
            
            meta_data.append(MetaData(
                deck_id=row[0],
                deck_name=row[1],
                deck_color=row[2],
                player_name=row[3],
                total_matches=total_matches,
                wins=wins,
                winrate=round(winrate, 2),
                meta_share=0  # Will be calculated below
            ))
        
        # Calculate meta share
        total_meta_matches = sum(deck.total_matches for deck in meta_data)
        for deck in meta_data:
            deck.meta_share = round((deck.total_matches * 100 / total_meta_matches), 2) if total_meta_matches > 0 else 0
        
        return meta_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)