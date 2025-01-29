from flask import Flask

app = Flask(__name__)

def cron():
    print("Cron job running")

if __name__ == '__main__':
    app.run()
