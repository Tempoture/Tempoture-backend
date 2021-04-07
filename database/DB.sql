-- We're not creating nonclustered indexes for things that use the spotify_id (if the ID is a varchar(255) variable) or if it's intermediate table--
-- TODO: We need to start removing the ignore_dup_keys and handling it in the code instead--
CREATE TABLE Genres(
    Genre varchar(50) NOT NULL,
    Genre_ID int  NOT NULL IDENTITY,
    PRIMARY KEY (Genre_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_Genre   
   ON Genres (Genre) WITH (IGNORE_DUP_KEY = ON);   

CREATE TABLE Users(
    Display_name text NOT NULL,
    Last_Known_Location_ID int NOT NULL,
    Home_Location_ID int  NOT NULL,
    numRuns smallint NOT NULL,
    numSongs smallint NOT NULL,
    numHours smallint NOT NULL,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    last_refreshed bigint NOT NULL,
    User_ID varchar(100) NOT NULL,
    PRIMARY KEY (User_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Songs_Artists(
    Song_ID varchar(100) NOT NULL,
    Artist_ID varchar(100) NOT NULL,
    UTC_Day_ID int NOT NULL,
    PRIMARY KEY (Song_ID,Artist_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE NONCLUSTERED INDEX IX_Songs_Artists
   ON Songs_Artists (UTC_Day_ID);

CREATE TABLE Genres_Artists(
    Genre_ID int  NOT NULL,
    Artist_ID varchar(100) NOT NULL,
    Confidence numeric(3,2) NOT NULL,
    UTC_Day_ID int NOT NULL,
    PRIMARY KEY (Artist_ID,Genre_ID,UTC_Day_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Songs_Playlists(
    Song_ID varchar(100) NOT NULL,
    Playlist_ID varchar(100) NOT NULL,
    UTC_Day_ID int NOT NULL,
    PRIMARY KEY (Song_ID,Playlist_ID) WITH (IGNORE_DUP_KEY = ON));


CREATE NONCLUSTERED INDEX IX_Songs_Playlists  
   ON Songs_Playlists (UTC_Day_ID);


CREATE TABLE Users_Playlists(
    User_ID varchar(100) NOT NULL,
    UTC_Day_ID int NOT NULL,
    Playlist_ID varchar(100) NOT NULL,
    PRIMARY KEY (User_ID,Playlist_ID) WITH (IGNORE_DUP_KEY = ON));


CREATE NONCLUSTERED INDEX IX_Users_Playlists  
   ON Users_Playlists (UTC_Day_ID);


CREATE TABLE Users_Artists(
    User_ID varchar(100) NOT NULL,
    UTC_Day_ID int NOT NULL,
    Artist_ID varchar(100) NOT NULL,
    PRIMARY KEY (User_ID,Artist_ID) WITH (IGNORE_DUP_KEY = ON));


CREATE NONCLUSTERED INDEX IX_Users_Artists  
   ON Users_Artists (UTC_Day_ID);


CREATE TABLE RecentlyPlayedSongs_User(
    Song_ID varchar(100) NOT NULL,
    User_ID varchar(100) NOT NULL,
    UTC_Day_ID int NOT NULL,
    PRIMARY KEY (Song_ID,User_ID) WITH (IGNORE_DUP_KEY = ON));


CREATE NONCLUSTERED INDEX IX_RecentlyPlayedSongs_User  
   ON RecentlyPlayedSongs_User (UTC_Day_ID);


CREATE TABLE Location(
    Location_ID int  NOT NULL IDENTITY,
    Zipcode varchar(10) NOT NULL,
    TimeZone_ID int,
    Country varchar(5) NOT NULL,
    PRIMARY KEY (Location_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_Location  
   ON Location (Zipcode,Country) WITH (IGNORE_DUP_KEY = ON);  

CREATE TABLE TimeZone(
    TimeZone_ID int NOT NULL IDENTITY,
    TimeZone_name varchar(50) NOT NULL,
    PRIMARY KEY (TimeZone_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE UNIQUE NONCLUSTERED INDEX IX_TimeZone   
   ON TimeZone (TimeZone_name) WITH (IGNORE_DUP_KEY = ON); 

CREATE TABLE DataCollectedPerHour(
    User_ID varchar(100) NOT NULL,
    Location_ID int  NOT NULL,
    UTC_Hour_ID int  NOT NULL,
    UTC_Day_ID int  NOT NULL,
    DataCollectedPerHour_ID int  NOT NULL IDENTITY,
    DataCollectedPerDate_ID int  NOT NULL,
    Weather_Characteristics_ID int ,
    PRIMARY KEY (DataCollectedPerHour_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_DataCollectedPerHour   
   ON DataCollectedPerHour (User_ID,UTC_Hour_ID,UTC_Day_ID) WITH (IGNORE_DUP_KEY = ON); 

CREATE TABLE DataCollectedPerDate(
    DataCollectedPerDate_ID int  NOT NULL IDENTITY,
    UTC_Day_ID int  NOT NULL,
    User_ID varchar(100) NOT NULL,
    PRIMARY KEY (DataCollectedPerDate_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_DataCollectedPerDate   
   ON DataCollectedPerDate (User_ID,UTC_Day_ID) WITH (IGNORE_DUP_KEY = ON);

CREATE TABLE UTC_Hour(
    UTC_Hour varchar(20) NOT NULL,
    UTC_Hour_ID int  NOT NULL IDENTITY,
    PRIMARY KEY (UTC_Hour_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_UTC_Hour  
   ON UTC_Hour (UTC_Hour) WITH (IGNORE_DUP_KEY = ON);

CREATE TABLE UTC_Day(
    UTC_Day varchar(20) NOT NULL,
    UTC_Day_ID int  NOT NULL IDENTITY,
    PRIMARY KEY (UTC_Day_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_UTC_Day  
   ON UTC_Day (UTC_Day) WITH (IGNORE_DUP_KEY = ON);

CREATE TABLE Time_Period(
    Time_Period_ID int NOT NULL IDENTITY,
    Time_Period varchar(20) NOT NULL,
    PRIMARY KEY (Time_Period_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_Time_Period  
   ON Time_Period (Time_Period) WITH (IGNORE_DUP_KEY = ON);

CREATE TABLE Location_UTC_Day_Hour(
    Location_ID int NOT NULL,
    UTC_Day_ID int NOT NULL,
    UTC_Hour_ID int NOT NULL,
    Sun_Position_ID smallint NOT NULL,
    PRIMARY KEY (Location_ID,UTC_Day_ID,UTC_Hour_ID));

CREATE TABLE Sun_Position(
    Sun_Position varchar(20) NOT NULL,
    Sun_Position_ID smallint NOT NULL IDENTITY,
    PRIMARY KEY (Sun_Position_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_Sun_Position  
   ON Sun_Position (Sun_Position) WITH (IGNORE_DUP_KEY = ON);

CREATE TABLE TimeZone_UTC_Hour(
    TimeZone_ID int  NOT NULL,
    UTC_Hour_ID int  NOT NULL,
    Time_Period_ID int  NOT NULL,
    PRIMARY KEY (TimeZone_ID,UTC_Hour_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Songs(
    Song_ID varchar(100) NOT NULL,
    danceability numeric(6,5) NOT NULL,
    acousticness numeric(6,5) NOT NULL,
    energy numeric(6,5) NOT NULL,
    Song_key smallint NOT NULL,
    loudness numeric(7,5) NOT NULL,
    mode bit NOT NULL,
    speechiness numeric(6,5) NOT NULL,
    instrumentalness numeric(6,5) NOT NULL,
    liveness numeric(6,5) NOT NULL,
    valence numeric(6,5) NOT NULL,
    tempo numeric(8,5) NOT NULL,
    duration_ms bigint NOT NULL,
    time_signature smallint NOT NULL,
    Song_name text NOT NULL,
    is_explicit bit not NULL,
    release_year smallint not NULL,
    popularity smallint NOT NULL,
    PRIMARY KEY (Song_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Song_Genres(
    Song_ID varchar(100)  NOT NULL,
    Genre_ID int NOT NULL,
    Confidence  numeric(7,5)  NOT NULL,
    PRIMARY KEY (Song_ID,Genre_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Artists(
    Artist_name text NOT NULL,
    Artist_ID varchar(100) NOT NULL,
    PRIMARY KEY (Artist_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Playlists(
    Playlist_name text NOT NULL,
    Playlist_ID varchar(100) NOT NULL,
    PRIMARY KEY (Playlist_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Genres_Playlists(
    Playlist_ID varchar(100) NOT NULL,
    Genre_ID int NOT NULL,
    Confidence numeric(7,5) NOT NULL,
    UTC_Day_ID int NOT NULL,
    PRIMARY KEY (Playlist_ID,Genre_ID,UTC_Day_ID) WITH (IGNORE_DUP_KEY = ON));

CREATE TABLE Weather_Characteristics(
    Weather_Characteristics_ID int NOT NULL IDENTITY,
    UTC_Day_ID int NOT NULL,
    UTC_Hour_ID int NOT NULL,
    Location_ID int NOT NULL,
    Temperature numeric(5,2) NOT NULL,
    Feels_like numeric(5,2) NOT NULL,
    pressure int NOT NULL,
    humidity numeric(5,2) NOT NULL,
    dew_point numeric(5,2) NOT NULL,
    cloudiness numeric(5,2) NOT NULL,
    visibility int NOT NULL,
    wind_speed numeric(5,2) NOT NULL,
    wind_gust numeric(5,2) ,
    wind_deg numeric(5,2) NOT NULL,
    rain numeric(5,2) ,
    snow numeric(5,2) ,
    conditions_id smallint NOT NULL,
    conditions text NOT NULL,
    PRIMARY KEY (Weather_Characteristics_ID));

CREATE UNIQUE NONCLUSTERED INDEX IX_Weather_Characteristics   
   ON Weather_Characteristics (Location_ID,UTC_Hour_ID,UTC_Day_ID) WITH (IGNORE_DUP_KEY = ON); 

CREATE TABLE DataCollectedPerHour_Songs(
    DataCollectedPerHour_ID int  NOT NULL,
    Song_ID varchar(100) NOT NULL,
    isNew bit NOT NULL,
    numPlayed smallint NOT NULL,
    PRIMARY KEY (DataCollectedPerHour_ID,Song_ID));

CREATE NONCLUSTERED INDEX IX_DataCollectedPerHour_Songs
    ON DataCollectedPerHour_Songs (isNew);

CREATE TABLE Users_Genres(
    User_ID varchar(100) NOT NULL,
    Genre_ID int NOT NULL,
    UTC_Day_ID int NOT NULL,
    Confidence numeric(7,5) NOT NULL
    PRIMARY KEY (User_ID,Genre_ID,UTC_Day_ID) WITH (IGNORE_DUP_KEY = ON));


ALTER TABLE Location_UTC_Day_Hour
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);


ALTER TABLE Location_UTC_Day_Hour
    ADD FOREIGN KEY (UTC_Hour_ID)
    REFERENCES UTC_Hour (UTC_Hour_ID);


ALTER TABLE Location_UTC_Day_Hour
    ADD FOREIGN KEY (Location_ID)
    REFERENCES Location (Location_ID);

ALTER TABLE Location_UTC_Day_Hour
    ADD FOREIGN KEY (Sun_Position_ID)
    REFERENCES Sun_Position (Sun_Position_ID);


ALTER TABLE Genres_Playlists
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);



ALTER TABLE Genres_Playlists
    ADD FOREIGN KEY (Genre_ID)
    REFERENCES Genres (Genre_ID);



ALTER TABLE Genres_Playlists
    ADD FOREIGN KEY (Playlist_ID)
    REFERENCES Playlists (Playlist_ID);



ALTER TABLE Genres_Artists
    ADD FOREIGN KEY (Genre_ID)
    REFERENCES Genres (Genre_ID);



ALTER TABLE Genres_Artists
    ADD FOREIGN KEY (Artist_ID)
    REFERENCES Artists (Artist_ID);



ALTER TABLE Genres_Artists
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);


ALTER TABLE Users_Playlists
    ADD FOREIGN KEY (User_ID)
    REFERENCES Users (User_ID);
    

ALTER TABLE Users_Artists
    ADD FOREIGN KEY (User_ID)
    REFERENCES Users (User_ID);


ALTER TABLE Users_Artists
    ADD FOREIGN KEY (Artist_ID)
    REFERENCES Artists (Artist_ID);


ALTER TABLE Users_Artists
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);
    


ALTER TABLE RecentlyPlayedSongs_User
    ADD FOREIGN KEY (User_ID)
    REFERENCES Users (User_ID);



ALTER TABLE Users
    ADD FOREIGN KEY (Last_Known_Location_ID)
    REFERENCES Location (Location_ID);
    


ALTER TABLE Users
    ADD FOREIGN KEY (Home_Location_ID)
    REFERENCES Location (Location_ID);
    


ALTER TABLE Location
    ADD FOREIGN KEY (TimeZone_ID)
    REFERENCES TimeZone (TimeZone_ID);
    


ALTER TABLE DataCollectedPerHour
    ADD FOREIGN KEY (DataCollectedPerDate_ID)
    REFERENCES DataCollectedPerDate (DataCollectedPerDate_ID);
    


ALTER TABLE DataCollectedPerHour
    ADD FOREIGN KEY (Location_ID)
    REFERENCES Location (Location_ID);
    


ALTER TABLE DataCollectedPerDate
    ADD FOREIGN KEY (User_ID)
    REFERENCES Users (User_ID);
    


ALTER TABLE DataCollectedPerDate
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);
    


ALTER TABLE DataCollectedPerHour
    ADD FOREIGN KEY (UTC_Hour_ID)
    REFERENCES UTC_Hour (UTC_Hour_ID);
    


ALTER TABLE DataCollectedPerHour
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);
    


ALTER TABLE TimeZone_UTC_Hour
    ADD FOREIGN KEY (TimeZone_ID)
    REFERENCES TimeZone (TimeZone_ID);
    


ALTER TABLE TimeZone_UTC_Hour
    ADD FOREIGN KEY (UTC_Hour_ID)
    REFERENCES UTC_Hour (UTC_Hour_ID);
    


ALTER TABLE TimeZone_UTC_Hour
    ADD FOREIGN KEY (Time_Period_ID)
    REFERENCES Time_Period (Time_Period_ID);
    


ALTER TABLE Songs_Artists
    ADD FOREIGN KEY (Song_ID)
    REFERENCES Songs (Song_ID);
    


ALTER TABLE Songs_Artists
    ADD FOREIGN KEY (Artist_ID)
    REFERENCES Artists (Artist_ID);


ALTER TABLE Songs_Artists
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);
    

ALTER TABLE Songs_Playlists
    ADD FOREIGN KEY (Song_ID)
    REFERENCES Songs (Song_ID);



ALTER TABLE Songs_Playlists
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);



ALTER TABLE Songs_Playlists
    ADD FOREIGN KEY (Playlist_ID)
    REFERENCES Playlists (Playlist_ID);


ALTER TABLE Weather_Characteristics
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);


ALTER TABLE Weather_Characteristics
    ADD FOREIGN KEY (UTC_Hour_ID)
    REFERENCES UTC_Hour (UTC_Hour_ID);


ALTER TABLE Weather_Characteristics
    ADD FOREIGN KEY (Location_ID)
    REFERENCES Location (Location_ID);

    
ALTER TABLE Song_Genres
    ADD FOREIGN KEY (Song_ID)
    REFERENCES Songs (Song_ID);


ALTER TABLE Song_Genres
    ADD FOREIGN KEY (Genre_ID)
    REFERENCES Genres (Genre_ID);


ALTER TABLE Users_Playlists
    ADD FOREIGN KEY (Playlist_ID)
    REFERENCES Playlists (Playlist_ID);



ALTER TABLE Users_Playlists
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);
    
    

ALTER TABLE RecentlyPlayedSongs_User
    ADD FOREIGN KEY (Song_ID)
    REFERENCES Songs (Song_ID);
    

ALTER TABLE RecentlyPlayedSongs_User 
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);



ALTER TABLE DataCollectedPerHour
    ADD FOREIGN KEY (Weather_Characteristics_ID)
    REFERENCES Weather_Characteristics (Weather_Characteristics_ID);
    
    


ALTER TABLE DataCollectedPerHour_Songs
    ADD FOREIGN KEY (DataCollectedPerHour_ID)
    REFERENCES DataCollectedPerHour (DataCollectedPerHour_ID);


ALTER TABLE Users_Genres
    ADD FOREIGN KEY (User_ID)
    REFERENCES Users (User_ID);


ALTER TABLE Users_Genres
    ADD FOREIGN KEY (Genre_ID)
    REFERENCES Genres (Genre_ID);


ALTER TABLE Users_Genres
    ADD FOREIGN KEY (UTC_Day_ID)
    REFERENCES UTC_Day (UTC_Day_ID);

