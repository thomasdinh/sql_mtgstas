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

| Column    | Type | Constraints                      |
| --------- | ---- | -------------------------------- |
| MatchID   | INT  | PRIMARY KEY                      |
| DeckLists | TEXT | NOT NULL                         |
| Date      | TEXT |                                  |
| WinnerID  | INT  | FOREIGN KEY (Deck(DeckID))       |
| GroupID   | INT  | FOREIGN KEY (Playgroup(groupID)) |

### DeckWin

| Column         | Type | Constraints                                    |
| -------------- | ---- | ---------------------------------------------- |
| MatchID        | INT  | PRIMARY KEY, FOREIGN KEY (MTGMatches(MatchID)) |
| DeckID         | INT  | PRIMARY KEY, FOREIGN KEY (Deck(DeckID))        |
| OpponentDeckID | TEXT |                                                |
| Result         | INT  | NOT NULL, CHECK (Result IN (0, 1, 2))          |
| Date           | TEXT | NOT NULL                                       |

0 - Draw
1 - Win
2 - Placeholder

### DeckLose

| Column         | Type | Constraints                                    |
| -------------- | ---- | ---------------------------------------------- |
| MatchID        | INT  | PRIMARY KEY, FOREIGN KEY (MTGMatches(MatchID)) |
| DeckID         | INT  | PRIMARY KEY, FOREIGN KEY (Deck(DeckID))        |
| OpponentDeckID | INT  |                                                |
| Result         | INT  | NOT NULL, CHECK (Result IN (0, 1, 2, 3))       |
| Date           | TEXT | NOT NULL                                       |

0 - Draw
1 - Lose
2,3 - Placeholder

## Indexes

- `idx_deck_owner` on `Deck(DeckOwnerID)`
- `idx_match_winner` on `MTGMatches(WinnerID)`
- `idx_deckwin_match` on `DeckWin(MatchID)`
- `idx_decklose_match` on `DeckLose(MatchID)`

# Database Schema for Playgroup Management

## Tables

### Playgroup

| Column    | Type      | Constraints | Description                     |
| --------- | --------- | ----------- | ------------------------------- |
| GroupID   | INT       | PRIMARY KEY | Unique identifier for the group |
| GroupName | CHAR(128) | NOT NULL    | Name of the playgroup           |

### PlaygroupPlayer

| Column   | Type | Constraints                          | Description                  |
| -------- | ---- | ------------------------------------ | ---------------------------- |
| GroupID  | INT  | PRIMARY KEY, FOREIGN KEY (Playgroup) | Identifier for the playgroup |
| PlayerID | INT  | PRIMARY KEY, FOREIGN KEY (Player)    | Identifier for the player    |

## Explanation

### Playgroup Table

- **GroupID**: A unique identifier for each playgroup.
- **GroupName**: The name of the playgroup, which cannot be null.

### PlaygroupPlayer Table

- **GroupID**: A foreign key referencing the `GroupID` in the `Playgroup` table.
- **PlayerID**: A foreign key referencing the `PlayerID` in the `Player` table.

The `PlaygroupPlayer` table serves as a junction table to establish a many-to-many relationship between playgroups and players. Each row in this table represents a player belonging to a specific playgroup.

## Example Usage

### Inserting Data

```sql
-- Insert into Playgroup table
INSERT INTO Playgroup (GroupID, GroupName) VALUES
(1, 'Group A'),
(2, 'Group B');

-- Insert into PlaygroupPlayer table
INSERT INTO PlaygroupPlayer (GroupID, PlayerID) VALUES
(1, 1), -- Player 1 is in Group A
(1, 2), -- Player 2 is in Group A
(2, 3), -- Player 3 is in Group B
(2, 4); -- Player 4 is in Group B
```
