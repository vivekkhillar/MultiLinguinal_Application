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
            service_status["database"] = "healthy"

        except Exception as e:
            service_status["database"] = "unhealthy"
            is_healthy = False
        
        try:
            await self.redis_manager.get_client().ping()
            service_status["redis"] = "healthy"

        except Exception as e:
            service_status["redis"] = "unhealthy"
            is_healthy = False

        payload = {

            "status"  :  "healthy" if is_healthy else "unhealthy",
            "services" : service_status
        }


        if not is_healthy:
            raise RuntimeError(payload)

        return payload

health_check = HealthCheck()
