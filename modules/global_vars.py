def init():
    global max_client_execution_time
    global resource_free_delay
    global reconnexion_retries
    max_client_execution_time = 0 # 0 means infinite
    resource_free_delay = 10
    reconnexion_retries = 10
