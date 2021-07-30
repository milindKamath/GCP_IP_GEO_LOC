from requests import get
import random
import json
import time
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from dotenv import load_dotenv
from flask import Flask, render_template
from google.cloud import secretmanager
app = Flask(__name__)
load_dotenv()


class PUBSUB:
    def __init__(self):
        self.project_id = "peak-emblem-319723"
        self.secret_id = "Service_account_key"
        self.version_id = "1"
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{self.project_id}/secrets/{self.secret_id}/versions/{self.version_id}"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        self.credentials = service_account.Credentials.from_service_account_info(json.loads(payload))
        self.topicName = "IP-GeoTag"
        self.publisher = None
        self.topicName_created = None
        self.dataJson = ""
        # self.credentials = service_account.Credentials.from_service_account_file(os.environ["KEY"])
        self.subscriptionName = "GeoTag_Sub"

    def create_pub_sub_topic(self):
        try:
            self.publisher = pubsub_v1.PublisherClient(credentials=self.credentials)
            self.topicName_created = 'projects/{project_id}/topics/{topic}'.format(
                project_id=self.project_id,
                topic=self.topicName,
            )

            self.publisher.create_topic(name=self.topicName_created)
        except:
            pass

    def callback(self, message):
        print("Message recevied from the topic", message.data)
        message.ack()

    def publish_to_topic(self):
        future = self.publisher.publish(self.topicName_created, str.encode(self.dataJson), dataFormat="json")
        future.result()

    def create_subscriber(self):
        try:
            self.subscriptionName = 'projects/{project_id}/subscriptions/{sub}'.format(
                project_id=self.project_id,
                sub=self.subscriptionName,
            )

            with pubsub_v1.SubscriberClient(credentials=self.credentials) as subscriber:
                try:
                    subscriber.create_subscription(
                        name=self.subscriptionName, topic=self.topicName_created)
                except:
                    future = subscriber.subscribe(self.subscriptionName, self.callback)
                    future.result(timeout=2)
        except:
            pass


class IP_to_LOC:

    def __init__(self):
        self.ip = ""
        self.NUM_HITS = 0
        self.result = None
        self.data = []

    def simulateIP(self):
        self.NUM_HITS = random.randint(1, 10)
        for i in range(self.NUM_HITS):
            self.ip = self.createIP()
            self.getInfo()

    def createIP(self):
        return ".".join(str(random.randint(0, 255)) for _ in range(4))

    def getInfo(self):
        try:
            self.result = get("http://ip-api.com/json/" +
                              self.ip + "?fields=status,message,continent"
                                        ",continentCode,country,countryCode"
                                        ",region,regionName,city,district,"
                                        "zip,lat,lon,timezone,offset,currency,"
                                        "isp,org,as,asname,reverse,mobile,proxy,hosting,query")
            if self.result.status_code == 200:
                content = json.loads(self.result.content)
                if content["status"] == "success":
                    self.data.append(content)
                else:
                    pass
            else:
                raise Exception
        except:
            ttl = int(self.result.headers["X-Ttl"])
            time.sleep(ttl)
            self.simulateIP()

    def getData(self):
        for inf in self.data:
            print(inf)


@app.route("/", methods=["GET"])
def startServer():
    return render_template("index.html")


@app.route("/ip", methods=["POST"])
def start():
    gen()
    return render_template("index.html")


def gen():
    ipLoc = IP_to_LOC()
    numIP = 0
    while numIP < 3:
        ipLoc.simulateIP()
        numIP += 1
    ps = PUBSUB()
    ps.dataJson = json.dumps(ipLoc.data)
    ps.create_pub_sub_topic()
    ps.create_subscriber()
    ps.publish_to_topic()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
