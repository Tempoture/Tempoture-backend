SELECT	K.Display_name,D.UTC_Day,C.Zipcode,C.Country,F.TimeZone_name,E.UTC_Hour,G.Sun_Position,I.Time_Period,J.isNew,J.numPlayed,L.Song_name
	FROM DataCollectedPerDate A inner join DataCollectedPerHour B on B.UTC_Day_ID = A.UTC_Day_ID 
								inner join Location C on B.Location_ID = C.Location_ID 
								inner join UTC_Day D on B.UTC_Day_ID = D.UTC_Day_ID 
								inner join UTC_Hour E on B.UTC_Hour_ID = E.UTC_Hour_ID
								inner join TimeZone F on F.TimeZone_ID = C.TimeZone_ID
								inner join Sun_Position G on G.Sun_Position_ID = B.SunPosition_ID
								inner join TimeZone_UTC_Hour H on H.TimeZone_ID = C.TimeZone_ID AND H.UTC_Hour_ID =B.UTC_Hour_ID
								inner join Time_Period I on I.Time_Period_ID = H.Time_Period_ID
								inner join DataCollectedPerHour_Songs J on J.DataCollectedPerHour_ID =B.DataCollectedPerHour_ID
								inner join Users K on K.User_ID =B.User_ID
								inner join Songs L on L.Song_ID = J.Song_ID;