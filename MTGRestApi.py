from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
import uvicorn
import mysql.connector
import pandas as pd
from datetime import datetime
import logging
import databaseinsql as dbsql
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MTG Match Analysis API",
    description="REST API for analyzing Magic: The Gathering multiplayer matches",
    version="1.0.0",
)

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Pydantic models
class PlayerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)

class Player(BaseModel):
    id: int
    name: str

class ConnectionStatus(BaseModel):
    connected: bool


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
    winner_deck_id: Optional[int] = None
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
@contextmanager
def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='mtgmatches2', 
            user='root', 
            password='101010',
            auth_plugin='mysql_native_password' 
        )
        yield connection
    finally:
        if connection is not None and connection.is_connected():
            connection.close()

@contextmanager
def exec_query(query, params=None, connection=None):
    cur_connection = connection
    if connection is None:
        cur_connection = get_connection()
    
    cursor = cur_connection.cursor()
    
    try:
        if params is None or len(params) == 0:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        
        yield cursor
        
        # Commit if we created our own connection
        if connection is None:
            cur_connection.commit()
            
    except Exception as e:
        # Rollback if we created our own connection
        if connection is None:
            cur_connection.rollback()
        raise e
        
    finally:
        cursor.close()
        # Close connection only if we created it
        if connection is None:
            cur_connection.close()


@app.get("/api/connection", response_model = ConnectionStatus )
async def check_connection():
    try:
        with get_connection() as connection:
            if connection.is_connected():
                return {"connected": True}
            else:
                raise HTTPException(status_code=503, detail="Database not connected")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
    

#Player
@app.get("/api/all_players", response_model=List[Player])
async def get_players():
    """Get all players"""
    try:
        with get_connection() as connection:
            with exec_query("SELECT PlayerID, Name FROM Player ORDER BY PlayerId",params= None, connection= connection) as cursor:
                players_result = cursor.fetchall()
                players = []
                for row in players_result:
                    player = Player(id=row[0], name=row[1])
                    print(f"Id: {row[0]} (Name: {row[1]})")
                    players.append(player)
                return players
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Player
@app.get("/api/player/{player_id}",response_model=Player)
async def get_player(player_id):
    try:
        with get_connection() as connection:
            with exec_query("SELECT PlayerID, Name FROM Player WHERE PlayerID = %s",params= [player_id], connection= connection) as cursor:
                
                result = cursor.fetchone()
                
                if result is None:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Player with ID {player_id} not found"
                    )
                print(result)
                return Player(id=result[0], name=result[1])
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
#Matches
@app.get("/api/matches", response_model=List[Match])
async def get_all_matches():
    try:
        with get_connection() as connection:
            with exec_query(query="SELECT * FROM MTGMatches", params= None, connection= connection) as cursor:
                result = cursor.fetchall()
                matches = []
                for row in result:

                    match = Match(id = row[0], deck_lists= row[1],
                                   date= row[2],
                                    winner_deck_id= row[3] if row[3] is not None else None,
                                      group_id= row[4] )
                    print(match)
                    matches.append(match)
                return matches

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )

# Run the application
if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)