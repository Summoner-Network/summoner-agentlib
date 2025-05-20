from summoner.server import SummonerServer

if __name__ == "__main__":
    srv = SummonerServer(name="Server")
    srv.run(config_path="server_config.json")
