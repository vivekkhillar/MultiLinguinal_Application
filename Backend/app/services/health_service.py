from core.lifespan import lifespan_instance

class HealthCheck:

    def __init__(self):
        self.database_manager = lifespan_instance.database_manager
        self.redis_manager = lifespan_instance.redis_manager
    

    async def check_health(self):

        try:
            await self.database_manager.ping()
            await self.redis_manager.get_client().ping()
            return {"status" : "ok", "message" : "Services are up and running"}

        except Exception as e:
            print(e)
            raise RuntimeError("Services are not up")

health_check = HealthCheck()
