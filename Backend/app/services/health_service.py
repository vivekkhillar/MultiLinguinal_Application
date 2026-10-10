from core.lifespan import lifespan_instance

class HealthCheck:

    def __init__(self):
        self.database_manager = lifespan_instance.database_manager
        self.redis_manager = lifespan_instance.redis_manager
        


    async def check_health(self):
        
        service_status = {}
        is_healthy = True 

        # Check data base is up and running
        try:
            await self.database_manager.ping()
            service_status["DataBase"] = "healthy"

        except Exception as e:
            service_status["Database"] = "unhealthy"
            is_healthy = False
        
        try:
            await self.redis_manager.get_client().ping()
            service_status["Redis"] = "healthy"

        except Exception as e:
            service_status["Redis"] = "unhealthy"
            is_healthy = False

        payload = {
            "status"  :  "Ok" if is_healthy else "error",
            "services" : service_status
        }

        return payload

health_check = HealthCheck()
