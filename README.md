[![WebAppCI/CD](https://github.com/software-students-fall2023/5-final-project-lastteam/actions/workflows/web-app.yml/badge.svg?branch=main)](https://github.com/software-students-fall2023/5-final-project-lastteam/actions/workflows/web-app.yml)

# Poker Analysis Pro

Build a containerized poker hand analysis app with CI/CD pipelines. See [instructions](./instructions.md) for details.

## [Live Demo](http://159.203.68.77:5001/)

Click on the above text to view the deployed demo!

## Team Members:

- [Merlin Li](https://github.com/wwxihan2)
- [Steven Li](https://github.com/stevenkhl446)
- [Zander Chen](https://github.com/ccczy-czy)

## Description:

Tracking poker profits and losses can be a tedious task, especially when trying to maintain data integrity and accuracy over an extended period. Poker Profit Tracker aims to solve this problem by providing a dedicated web application that allows poker players to systematically record, track, and analyze their gaming sessions. PPTp will facilitate users to register, login, and manage their poker session data seamlessly, with an easy-to-use and intuitive interface that focuses on user experience and data accuracy along with integration of other external APIs.

## Setup:

### Prerequisites:

Before you start the steps below, make sure you have the following downloaded on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running the Application:

1. Clone the repository:

```
git clone https://github.com/software-students-fall2023/5-final-project-lastteam.git
```

2. Navigate to the project directory:

```
cd 5-final-project-lastteam
```

3. Build docker images and run the containers:

```
docker compose up --build -d
```

4. Open the application in your browser:

```
http://localhost:5001
```

5. To stop the containers, run the command:

```
docker compose down
```
