from infrastructure.redis.connection import RedisConnectionManager
import asyncio

async def main():

    # Create a object of the class redid
    redis = RedisConnectionManager()

    # try connect to redis
    await redis.connect()

    # Create a client of the redis
    client = redis.get_client()

    # check the client 
    print (await client.ping())

    # close the client
    await redis.close()

if __name__ == "__main__":
    
    asyncio.run(main())