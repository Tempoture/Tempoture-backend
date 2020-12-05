<!--[![GPL License][license-shield]][license-url] -->
Tempoture is an application designed to link users to a playlist based on the current weather in their area.
The main goal is to be able to correlate user listening habits to the change in weather through the use of a machine learning model.

<br />
<p align="center">
  <a href="https://github.com/Tempoture/Tempoture-backend">
     <img src="https://cdn.discordapp.com/attachments/750506956539822120/769965690420723722/LOGO.PNG" alt="Logo" width="350" height="350">
  </a> 
   <h3 align="center">Backend and Database for the Tempoture Project</h3>

  <p align="center">
    <a href="https://github.com/Tempoture/"><strong>Repositories for Tempoture</strong></a>
    <br />
    <a href="https://github.com/Tempoture/Tempoture-frontend">Frontend Repository</a>
    ·
    <a href="https://github.com/Tempoture/Tempoture-backend">Backend and Database Repository</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Backend](#About-The-Backend)
  * [Software](#BackendSoftware)
  * [Installation Guide](#Backend-Installation-Guide)
* [About the Database](#About-The-Database)
  * [Software](#DatabaseSoftware)
  * [Installation Guide](#Database-Installation-Guide)
    * [Flask](#Flask)
    * [Psycopg2](#Psycopg2)
    * [PostgreSQL](#PostgreSQL)
    * [SQLAlchemy](#SQLAlchemy)
* [License](#License)
* [Useful Resources](#Useful-Resources)
  * [Backend](#Backend-Resources)
  * [Database](#Database-Resources)
# Backend

This portion of the repository was made for the backend. 
![Tempoture Logo](https://cdn.discordapp.com/attachments/750506956539822120/769965690420723722/LOGO.PNG "Tempoture Logo")

## API Reference

The Tempoture backend will make use of three APIs:

1. [IP Geo Location](https://ipgeolocation.io/ "IP Geo Location")

2. [OpenWeather](https://openweathermap.org/api " OpenWeather")

3. [Spotify - User Recently Played Songs](https://developer.spotify.com/documentation/web-api/reference/player/get-recently-played/ "Spotify - User Recently Played Songs")

# Database
<!-- ABOUT THE Database -->
## About The Database

<br />
  <p align="center">
    <img src="https://cdn.discordapp.com/attachments/750506956539822120/775842802964627486/schema.PNG" alt="Logo" width="800" height="400">
  </p>
<br />

Above is a physical representation of the database that is used for the Tempoture project. The SQL to make this database can be found [here](https://github.com/Tempoture/Tempoture-Data-Base/blob/main/SQL-Queries/TempoDB_V1.sql). This database is used to store user data, Spotify music data, and local weather data. 
  <!-- fill this in -->
  
  
<!-- Software -->
### Software
  <!-- fill this in -->
  
  <!--turn into link-->
  * [Vertabelo](https://vertabelo.com/) - An application used for designing database schema.
  * [PGAdmin](https://www.pgadmin.org/) - A software used for database maintenance and running queries. 
  * [Psycopg2](https://pypi.org/project/psycopg2/) - A software used with python to establish connections with databases.  
  * [PostgreSQL](https://www.postgresql.org/) - An open source object-relational database system that uses and extends the SQL language.
  * [Python3](https://www.python.org/download/releases/3.0/) - The programming language of choice for the project. 
  * [SQLAlchemy](https://www.sqlalchemy.org/) - The software used in conjunction with Psycopg2 to query the database.
  
<!-- Installation -->
## Installation Guide
Before installing the following softwares, have the latest version of Python installed. Also note that these install commands are specific for the Ubuntu bash terminal. 
  ### Flask
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt update` - Ensures Ubuntu is up to date.
   <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt install python3-pip` - Install package management system.
   <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$pip install Flask` - Install for Flask.
    
  ### Psycopg2
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt update` - Ensures Ubuntu is up to date.
   <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt install python3-pip` - Install package management system.
   <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$pip install psycopg2` - Install for psycopg2.
    
  ### PostgreSQL
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt update` - Ensures Ubuntu is up to date.
  <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt-get install postgresql postgresql-contrib`<br>
  
  ### SQLAlchemy
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$sudo apt update` - Ensures Ubuntu is up to date.
  <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`$pip install SQLAlchemy` - Install for SQL alchemy.
  
<!-- Useful Resources -->
## Useful Resources
* [MySQL in 25 Minutes](https://www.youtube.com/watch?v=8kDs8QkFI2Y&list=PLB-7_zmcEzQyjWl5g8KBnd3dKRvmRlSYA&index=11)
* [How to Design a Database](https://www.youtube.com/watch?v=cepspxPAUTA&list=PLB-7_zmcEzQyjWl5g8KBnd3dKRvmRlSYA&index=1)
* [Logical Database Design](https://www.youtube.com/watch?v=ZBgXb66Ckz0&list=PLB-7_zmcEzQyjWl5g8KBnd3dKRvmRlSYA&index=15)
* [Database Design Course](https://www.youtube.com/watch?v=ztHopE5Wnpc)
* [Intro to PostgreSQL with PgAdmin](https://www.youtube.com/watch?v=Dd2ej-QKrWY)
* [AES Explained (Advanced Encryption Standard)](https://www.youtube.com/watch?v=O4xNJsjtN6E)
  
<!-- License -->
# License
  Distributed under the GPL License. See `LICENSE` for more information.
<!-- links -->
[license-shield]: https://cdn.discordapp.com/attachments/750506956539822120/771468904899543090/gpl_license.PNG
[license-url]: https://github.com/Tempoture/Tempoture-Data-Base/blob/main/LICENSE
