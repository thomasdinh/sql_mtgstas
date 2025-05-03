--@block
CREATE TABLE Player (
    PlayerID INT PRIMARY KEY,
    Name CHAR(128) NOT NULL
);
--@block
CREATE TABLE Deck (
    DeckID INT PRIMARY KEY,
    DeckName CHAR(128) NOT NULL,
    DeckOwnerID INT,
    DeckImgURL TEXT,
    DeckColor CHAR(32),
    DeckURL TEXT,
    FOREIGN KEY (DeckOwnerID) REFERENCES Player(PlayerID)
);
--@block
CREATE TABLE MTGMatches (
    MatchID INT PRIMARY KEY,
    DeckLists TEXT NOT NULL,
    Date TEXT,
    WinnerID INT,
    FOREIGN KEY (WinnerID) REFERENCES Deck(DeckID)
);
--@block
CREATE TABLE DeckWin (
    MatchID INT,
    DeckID INT,
    OpponentDeckID TEXT,
    -- (List of opponents lost: 2,3,4)
    Result INT NOT NULL,
    Date TEXT NOT NULL,
    PRIMARY KEY (MatchID, DeckID),
    FOREIGN KEY (MatchID) REFERENCES MTGMatches(MatchID),
    FOREIGN KEY (DeckID) REFERENCES Deck(DeckID)
);
--@block
CREATE TABLE DeckLose (
    MatchID INT,
    DeckID INT,
    OpponentDeckID INT,
    Result INT NOT NULL,
    Date Text NOT NULL,
    PRIMARY KEY (MatchID, DeckID),
    FOREIGN KEY (MatchID) REFERENCES MTGMatches(MatchID),
    FOREIGN KEY (DeckID) REFERENCES Deck(DeckID)
);
--@block
CREATE INDEX idx_deck_owner ON Deck(DeckOwnerID);
CREATE INDEX idx_match_winner ON MTGMatches(WinnerID);
CREATE INDEX idx_deckwin_match ON DeckWin(MatchID);
CREATE INDEX idx_decklose_match ON DeckLose(MatchID);
--@block
ALTER TABLE DeckWin
ADD CONSTRAINT chk_result CHECK (Result IN (0, 1, 2));
-- 1 for win, 2 for draw, 0 for loss
--@block
ALTER TABLE DeckLose
ADD CONSTRAINT chk_lose_result CHECK (Result IN (0, 1, 2, 3));
-- 1 for win, 2 for draw, 0 for loss