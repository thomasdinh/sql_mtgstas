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
SELECT *
FROM mtgmatches --@block
    -- Insert into Player table
INSERT INTO Player (PlayerID, Name)
VALUES (1, 'Thomas'),
    (2, 'Peter'),
    (3, 'Kristian'),
    (4, 'Leon'),
    (5, 'Khang'),
    (6, 'Olli'),
    (7, 'Steven'),
    (8, 'Hoang');
--@block
CREATE TABLE Playgroup (
    GroupID INT PRIMARY KEY,
    GroupName CHAR(128) NOT NULL
);
CREATE TABLE PlaygroupPlayer (
    GroupID INT,
    PlayerID INT,
    PRIMARY KEY (GroupID, PlayerID),
    FOREIGN KEY (GroupID) REFERENCES Playgroup(GroupID),
    FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID)
);
INSERT INTO Playgroup (GroupID, GroupName)
VALUES (1, 'Wartenberg Group'),
    (2, 'Leon Group');
--@block
INSERT INTO Deck (
        DeckID,
        DeckName,
        DeckOwnerID,
        DeckImgURL,
        DeckColor,
        DeckURL
    )
VALUES (
        1,
        'Aesi',
        3,
        'https://cards.scryfall.io/art_crop/front/6/7/673c21f8-02b6-4ac4-b2fc-df065b4ac662.jpg?1726285172',
        '{4}GU',
        NULL
    );
--@block
INSERT INTO Deck (
        DeckID,
        DeckName,
        DeckOwnerID,
        DeckImgURL,
        DeckColor,
        DeckURL
    )
VALUES (
        2,
        'Animar',
        8,
        'https://cards.scryfall.io/art_crop/front/a/3/a3da57d0-1ae3-4f05-a52d-eb76ad56cae7.jpg?1673148281',
        'GUR',
        NULL
    );
--@block
INSERT INTO Deck (
        DeckID,
        DeckName,
        DeckOwnerID,
        DeckImgURL,
        DeckColor,
        DeckURL
    )
VALUES (
        3,
        'Arna',
        5,
        'https://cards.scryfall.io/large/front/3/3/33228a89-0276-4e5e-9956-382f1628e351.jpg?1717201730',
        '{3}BUW',
        NULL
    ),
    (
        4,
        'Atla',
        2,
        'https://cards.scryfall.io/art_crop/front/2/b/2b8414f7-22c3-4e1c-934b-4a0e7acf951d.jpg?1673305450',
        'RGW',
        NULL
    ),
    (
        5,
        'Atraxa',
        4,
        'https://cards.scryfall.io/art_crop/front/d/0/d0d33d52-3d28-4635-b985-51e126289259.jpg?1599707796',
        'WUBG',
        NULL
    ),
    (
        6,
        'Baylen',
        8,
        'https://cards.scryfall.io/art_crop/front/0/0/00e93be2-e06b-4774-8ba5-ccf82a6da1d8.jpg?1721427006',
        'RGW',
        NULL
    ),
    (
        7,
        'Betor',
        8,
        'https://cards.scryfall.io/art_crop/front/2/e/2e261489-8dde-4594-8868-69f432f03d03.jpg?1745970934',
        '{2}WGB',
        NULL
    ),
    (
        8,
        'Chulane',
        2,
        'https://cards.scryfall.io/art_crop/front/d/1/d1499a4b-1af1-4913-8e26-57d0707264db.jpg?1706240978',
        'GWU',
        NULL
    ),
    (
        9,
        'Coram',
        2,
        'https://cards.scryfall.io/art_crop/front/a/b/ab5cfb0c-8e95-4d2d-9e23-cf58c1c7e51c.jpg?1727175651',
        '{1}BRG',
        NULL
    ),
    (
        10,
        'Edgar',
        6,
        'https://cards.scryfall.io/art_crop/front/a/5/a577ba08-0aa8-45be-aa83-d5078770127c.jpg?1736468492',
        '{3}RWB',
        NULL
    );
--@block
INSERT INTO Deck (
        DeckID,
        DeckName,
        DeckOwnerID,
        DeckImgURL,
        DeckColor,
        DeckURL
    )
VALUES (
        11,
        'Eluge',
        6,
        'https://cards.scryfall.io/art_crop/front/d/f/df9da428-3af7-4027-b3f0-9138d953c37b.jpg?1721427536',
        '{1}UUU',
        NULL
    ),
    (
        12,
        'Etali',
        1,
        'https://cards.scryfall.io/art_crop/front/9/5/95c14c4d-6c16-4826-8d93-d89ad04aee09.jpg?1739657577',
        '{5}RR',
        NULL
    ),
    (
        13,
        'Feather',
        3,
        'https://cards.scryfall.io/art_crop/front/d/7/d763695b-c184-409d-962d-5aaf39a6264e.jpg?1706448890',
        'RWW',
        NULL
    ),
    (
        14,
        'Ghired',
        1,
        'https://cards.scryfall.io/art_crop/front/e/4/e43e3d71-4fb8-4ab1-8c8f-b65ae3ad4cc4.jpg?1712356098',
        'RGW',
        NULL
    ),
    (
        15,
        'Giada',
        3,
        'https://cards.scryfall.io/art_crop/front/b/a/bae077bd-fc8d-44d7-8c75-8dc8699c168e.jpg?1664409667',
        '{2}W',
        NULL
    ),
    (
        16,
        'Gitrog',
        2,
        'https://cards.scryfall.io/art_crop/front/8/2/82512813-8618-483b-a7f0-e6a611d9d487.jpg?1712356103',
        '{3}BG',
        NULL
    ),
    (
        17,
        'Hashaton',
        2,
        "https://cards.scryfall.io/art_crop/front/0/2/02645651-cd55-4bd0-8a4d-fa257270a0e0.jpg?1747231831",
        'WB',
        NULL
    ),
    (
        18,
        'Henzie',
        3,
        'https://cards.scryfall.io/art_crop/front/e/e/ee228dcc-3170-4c24-80bc-28bcee07cb43.jpg?1673481644',
        'BRG',
        NULL
    ),
    (
        19,
        'Ixhel',
        3,
        'https://cards.scryfall.io/art_crop/front/a/b/ab866ec4-dcb4-47ef-8de1-a369986609c0.jpg?1738281205',
        '{1}WBG',
        NULL
    ),
    (
        20,
        'Jodah',
        2,
        'https://cards.scryfall.io/art_crop/front/d/c/dca766a6-9a35-4079-b014-583daadda7f8.jpg?1675619592',
        'WUBRG',
        NULL
    ),
    (
        21,
        'Kaalia',
        3,
        'https://cards.scryfall.io/art_crop/front/5/7/576a670d-4efd-498b-8c53-eda6e18868a4.jpg?1681411770',
        'RWB',
        NULL
    ),
    (
        22,
        'Kalamax',
        4,
        'https://cards.scryfall.io/art_crop/front/f/9/f990cd78-2165-446f-a116-ae55d7a0f00d.jpg?1591234251',
        '{1}URG',
        NULL
    ),
    (
        23,
        'Kinnan',
        6,
        'https://cards.scryfall.io/art_crop/front/6/3/63cda4a0-0dff-4edb-ae67-a2b7e2971350.jpg?1591228085',
        'UG',
        NULL
    ),
    (
        24,
        'Light-Paws',
        7,
        'https://cards.scryfall.io/art_crop/front/3/9/39555a72-a57b-45ee-9222-ce3b9e8de126.jpg?1654566391',
        'W',
        NULL
    ),
    (
        25,
        'Marrow-Gnawer',
        2,
        'https://cards.scryfall.io/art_crop/front/7/2/72e4548b-c171-4f10-b896-af37543dcf0f.jpg?1579203069',
        '{3}BB',
        NULL
    ),
    (
        26,
        'Mishra',
        1,
        'https://cards.scryfall.io/art_crop/front/c/4/c4f17db9-4ca2-43bd-b4a3-8d862a7bc9cc.jpg?1674099632',
        '{2}UBR',
        NULL
    ),
    (
        27,
        'Morophon',
        3,
        'https://cards.scryfall.io/art_crop/front/8/4/84238335-e08c-421c-b9b9-70a679ff2967.jpg?1689995411',
        '{7}',
        NULL
    ),
    (
        28,
        'Narci',
        3,
        'https://cards.scryfall.io/art_crop/front/a/9/a98a2fa9-82d6-4cf7-adb4-65b187cd9cda.jpg?1691497812',
        'WBG',
        NULL
    ),
    (
        29,
        'Obeka',
        8,
        'https://cards.scryfall.io/art_crop/front/0/3/03415c42-086e-4a2e-9be8-5cdcde83f134.jpg?1712356168',
        'UBR',
        NULL
    ),
    (
        30,
        'Omnath',
        1,
        'https://cards.scryfall.io/art_crop/front/9/a/9a0a9d3f-cd75-419b-840f-88b468f71f4a.jpg?1712354757',
        'WUBRG',
        NULL
    ),
    (
        31,
        'Otharri',
        2,
        'https://cards.scryfall.io/art_crop/front/8/0/80c72839-0fa6-4b5f-83b7-6553ebf09bef.jpg?1738281232',
        'WR',
        NULL
    ),
    (
        32,
        'Pantlaza',
        1,
        'https://cards.scryfall.io/art_crop/front/2/5/2524645e-b066-4351-885b-10faa8d819d7.jpg?1699972737',
        'WRG',
        NULL
    ),
    (
        33,
        'Prosper',
        4,
        'https://cards.scryfall.io/art_crop/front/d/7/d743336e-d5c7-4053-a23d-92ec7581f74e.jpg?1631839207',
        'BR',
        NULL
    ),
    (
        34,
        'Radagast',
        3,
        'https://cards.scryfall.io/art_crop/front/b/3/b3988120-ebbe-4d24-9bb4-8c5331a14034.jpg?1686969557',
        'G',
        NULL
    ),
    (
        35,
        'Rocco',
        3,
        'hhttps://cards.scryfall.io/art_crop/front/b/6/b6cf8b35-2a81-40fd-b383-becb81bef806.jpg?1664413683',
        'RGW',
        NULL
    ),
    (
        36,
        'Saheeli',
        1,
        'https://cards.scryfall.io/art_crop/front/c/a/ca095559-ac77-4186-8d9b-b75ce0607582.jpg?1592710284',
        'UR',
        NULL
    ),
    (
        37,
        'Sythis',
        6,
        'https://cards.scryfall.io/art_crop/front/8/9/89511ab5-8ea6-4f07-a80b-c1ec7e89924e.jpg?1690005342',
        'GW',
        NULL
    ),
    (
        38,
        'Tahngarth',
        1,
        'https://cards.scryfall.io/art_crop/front/1/6/1692c11b-018e-47bf-b38d-3c3e6b79b37c.jpg?1568003736',
        'RG',
        NULL
    ),
    (
        39,
        'Temmet',
        1,
        'https://cards.scryfall.io/art_crop/front/c/0/c0629894-0b72-4abe-9771-03becfdb241c.jpg?1747231842',
        'WUB',
        NULL
    ),
    (
        40,
        'Tymna',
        3,
        'https://cards.scryfall.io/art_crop/front/b/c/bc7cbe9b-324e-42b8-94e2-36e91cb32163.jpg?1644853048',
        'WB',
        NULL
    ),
    (
        41,
        'Ulalek',
        2,
        'https://cards.scryfall.io/art_crop/front/f/d/fdad1b0e-d3cc-4d76-ae7e-fee12558cf2c.jpg?1735676761',
        'C',
        NULL
    ),
    (
        42,
        'Urza',
        1,
        'https://cards.scryfall.io/art_crop/front/e/a/ea409050-4296-4b76-a6cd-2896ce1b88e4.jpg?1705542672',
        'WUB',
        NULL
    ),
    (
        43,
        'Voja',
        6,
        'https://cards.scryfall.io/art_crop/front/b/f/bfa1bd2f-25bd-4fbd-877b-cef00ab7f92f.jpg?1707739811',
        'RG',
        NULL
    ),
    (
        44,
        'Wilhelt',
        8,
        'https://cards.scryfall.io/art_crop/front/2/5/2501a911-d072-436d-ae3b-a5164e3b30aa.jpg?1675456154',
        'UB',
        NULL
    ),
    (
        45,
        'Xyris',
        1,
        'https://cards.scryfall.io/art_crop/front/a/f/af0db1d6-5cb1-4917-8e8f-69d5dc184404.jpg?1673305716',
        'URG',
        NULL
    ),
    (
        46,
        'Yarok',
        6,
        'https://cards.scryfall.io/art_crop/front/a/1/a1001d43-e11b-4e5e-acd4-4a50ef89977f.jpg?1722108823',
        'UBG',
        NULL
    ),
    (
        48,
        'Obeka 2',
        8,
        'https://cards.scryfall.io/art_crop/front/0/3/03415c42-086e-4a2e-9be8-5cdcde83f134.jpg?1712356168',
        'UBR',
        NULL
    ),
    (
        47,
        'Yedora',
        2,
        'https://cards.scryfall.io/art_crop/front/7/b/7b852b55-bee1-46fc-87e4-5c01b90bbd43.jpg?1726514214',
        'G',
        NULL
    );