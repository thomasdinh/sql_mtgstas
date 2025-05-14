# Database Schema Diagram

## Tables

### Player

| Column   | Type      | Constraints |
| -------- | --------- | ----------- |
| PlayerID | INT       | PRIMARY KEY |
| Name     | CHAR(128) | NOT NULL    |

### Deck

| Column      | Type      | Constraints                    |
| ----------- | --------- | ------------------------------ |
| DeckID      | INT       | PRIMARY KEY                    |
| DeckName    | CHAR(128) | NOT NULL                       |
| DeckOwnerID | INT       | FOREIGN KEY (Player(PlayerID)) |
| DeckImgURL  | TEXT      |                                |
| DeckColor   | CHAR(32)  |                                |
| DeckURL     | TEXT      |                                |

### MTGMatches

| Column    | Type | Constraints                |
| --------- | ---- | -------------------------- |
| MatchID   | INT  | PRIMARY KEY                |
| DeckLists | TEXT | NOT NULL                   |
| Date      | TEXT |                            |
| WinnerID  | INT  | FOREIGN KEY (Deck(DeckID)) |

### DeckWin

| Column         | Type | Constraints                                    |
| -------------- | ---- | ---------------------------------------------- |
| MatchID        | INT  | PRIMARY KEY, FOREIGN KEY (MTGMatches(MatchID)) |
| DeckID         | INT  | PRIMARY KEY, FOREIGN KEY (Deck(DeckID))        |
| OpponentDeckID | TEXT |                                                |
| Result         | INT  | NOT NULL, CHECK (Result IN (0, 1, 2))          |
| Date           | TEXT | NOT NULL                                       |

### DeckLose

| Column         | Type | Constraints                                    |
| -------------- | ---- | ---------------------------------------------- |
| MatchID        | INT  | PRIMARY KEY, FOREIGN KEY (MTGMatches(MatchID)) |
| DeckID         | INT  | PRIMARY KEY, FOREIGN KEY (Deck(DeckID))        |
| OpponentDeckID | INT  |                                                |
| Result         | INT  | NOT NULL, CHECK (Result IN (0, 1, 2, 3))       |
| Date           | TEXT | NOT NULL                                       |

## Indexes

- `idx_deck_owner` on `Deck(DeckOwnerID)`
- `idx_match_winner` on `MTGMatches(WinnerID)`
- `idx_deckwin_match` on `DeckWin(MatchID)`
- `idx_decklose_match` on `DeckLose(MatchID)`
