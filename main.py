from scheduler import app


if __name__ == "__main__":

    if app.config["ENV"] == "development":
        app.run(host="0.0.0.0")
    else:
        app.run()
