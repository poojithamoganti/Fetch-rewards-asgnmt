Installations:
Step 1: Install Docker & Docker compose
Step 2: Install Awscli for windows 
Step 3: Go to terminal and install "pip install awscli-local"
Step 4: Install Postqresql 

Implementation:

Step 1: create a folder , create a docker-compose.yml file and open it in VScode
Step 2: Write connections for localstack and postgres (make sure you have open Docker desktop)
Step 3: docker pull localstack and postgres images in terminal.( docker pull fetchdocker/data-takehome-postgres:latest , docker pull fetchdocker/data-takehome-localstack:latest)
step 4: docker-compose config to check if any errors in yml file.
Step 5: Run docker-compose up to start container 
Step 6 : create a directory call app in project and add a python file to it.
Step 7: Add/Install boto3 and psycopg2 libraries.
Step 8: Write down connections , transfoemations , aws credintials properly in code.
Step 9: Open new terminal and run your python code (make sure your in correct directory)
Step 10: Create a new file init.sql to create a table user_logins in postgres
Step 11: to create table and run init.sql open new terminal and run "psql -U postgres -d postgres -f "path\init.sql" "
Step 12: To verify if the table is created run "psql -U postgres -d postgres -p 5432 -h localhost -W" , enter password.
Step 13: After entering into postgres run "Select * from user_logins;" to check data.
Step 14: Run " awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue" 
Step 15: Type in "localhost:4566/login-queue" in browser to check.


Decisions made to develop this solutions:

1. To read messages from the AWS SQS queue i used boto3 library in python.And I've used "receive - message" method to fetch the messages from the queue.

2. For processing the messages, i used Python dictionaries to represent the JSON data received from SQS queue as these are efficent for working with structured data, and it will allow easy access to individual fields for masking and writing to the database.

3.To mask tge PII data for device_id and ip fields , i used a hash function to convert the orginal values into masked values.The objective is to mask the data in a way that maintains consistency for duplicate values, so that data analysts can still identify duplicates while protecting senstive information.

4.To connect with PostgreSQL database, I have used "psycopg2" library. It is a widely used python adapter allowing easy interaction with the database.i have then established a connection and used prepared statement/batch inserts to efficiently write the masked data into "user_logins" table.

5. For the application deployment, I have considered two options:
   1. Local deployment (Development & testing) : I will run the application locally on my machine using Docker for local PostgresSQL and Localstack for the SQS      	queue emulator. To manage the containers and set up the environment i will use Docker compose. 
   2. Cloud deployment(Production) : I will deploy this application in a cloud platform such as AWS using services like Lambda for 	serverless execution , SQS for the queue  and RDS for PostgreSQL database.  


Questions:

1. To deploy this application in production , we can consider:
	a. Package the application and its dependencies into containers using docker (Containerization). This will ensure consistent 			deployments across different environments.
	b. Using Kubernetes or AWS ECS which are container orchestration systems to manage the deployment , scaling and availabilty of the 		application
	c. Setting up a CI/CD pipelines to automate testing and ensuring smooth updates and rollbacks.


2. The other components i want to add are:
	. AWS cloudwatch for logging and monitoring
	. Backup and Disaster recovery plan
	. AWS Secrets manager to store senstive information more securely.

3. For Scaling with growing dataset , I would like to do Horizontal Scaling(Auto scaling) and Partitioning to enable efficient data 	retrieval by distributing data across multiple nodes. 

4. For PII recovery in future i would use Pseudonymization , which allows to reconstruct data using Key or mapping.

5. According to my assumptions , the application assumes the JSON data received from SQS contains expected fields for processing.But there 	might be null / empty values. For which error handling must be needed. we must assure that PostgreSQl and AWS connections , 	username , password / credientials must be specified properly.















