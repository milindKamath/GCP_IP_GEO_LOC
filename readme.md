## IP Geo Location

>> Pipeline 

![](https://github.com/milindKamath/GCP_IP_GEO_LOC/blob/9e2e6aaba38466ff6259caa02cbdfdefd58ce05d/IP%20geolocation.png)

>> Pipeline Steps:

1. Get Request from IP to location api and simulate web hits.

2. Flask server to create a web server to start the simulation.

3. Service Account for minimal PUBSUB permissions.

4. Creating a PUBSUB topic, subscribers and publishing message to the topic.

5. Docker build using Dockerfile and push image to google cloud container registry.

6. Create cloud run service to run the docker image with an http endpoint.
Keys for the service account are saved into secrets manager and accessed from the code.

7. Create a service account for minimal permissions for composer and big query.

8. Create a composer using the service account with api authenticate backend key value.

9. Get the airflow client id, webserver id.

10. Create cloud function which triggers airflow dag when a message is published to the topic.

11. Trigger function triggers dag using the airflow ids from previous step.

12. Create a python dag file to pull message from pubsub and insert into big query.

13. Using Data studio, create dashboard for visualization.
