[![WebAppCI/CD](https://github.com/software-students-fall2023/5-final-project-lastteam/actions/workflows/web-app.yml/badge.svg?branch=main)](https://github.com/software-students-fall2023/5-final-project-lastteam/actions/workflows/web-app.yml)

# Badge

# Links to container images

# Poker Profit Tracker Pro 

# team member names

- ![Steven](https://github.com/stevenkhl446) 
- ![Merlin](https://github.com/wwxihan2) 
- ![Zander](https://github.com/ccczy-czy) 


## Overview

Tracking poker profits and losses can be a tedious task, especially when trying to maintain data integrity and accuracy over an extended period. Poker Profit Tracker aims to solve this problem by providing a dedicated web application that allows poker players to systematically record, track, and analyze their gaming sessions. PPTp will facilitate users to register, login, and manage their poker session data seamlessly, with an easy-to-use and intuitive interface that focuses on user experience and data accuracy along with integration of other external API(news parser).

## Data Model

The application will primarily involve the management of Users and Poker Sessions, with a relation linking users to multiple sessions.

Users can have multiple poker sessions (via references).
Each session will hold detailed information about the gaming activity.

An Example User:

{
  username: "poker_pro123",
  hash: // a password hash,
  sessions: // an array of references to Poker Session documents
}
```

An Example Poker Session:

{
  user: // a reference to a User object,
  buyIn: Number, //buy in amount
  date: Date, //date
  cashOut: Number, //cash out amount
  profit: Number, //cash out -buy in
  highlights: String,//not needed
  location: String //location of the session
}

```
Poker Main(home)
Menu: Sessions
          view sessions(list of all sessions created)
          create a session(to create a session)
       Search
          Search session by either (date, buyin, location, or profit/loss)
       User Settings
          change Password
          change Username
          Delete Account(this will delete the account from the database)
       log out
          log out from Poker Profit Tracker Pro

Links to all 

# User Stories or Use Cases

1. As a non-registered user, I can register a new account with the site.
2. As a user, I can log in to the site.
3. As a user, I can create or delete a poker session.
4. As a user, I can view a summary of all my poker sessions in graphs.
5. As a user, I can view or create detailed information of each poker session.
6. As a user, I can change user informations.
8. As a user, I can view the latest poker news.

# instructions to run

# Starter data demo

create user name and password as you wish, and create as many sessions for poker. Make sure you are logged in before using any features.
