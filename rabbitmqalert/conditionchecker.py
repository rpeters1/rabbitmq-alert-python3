
class ConditionChecker:

    def __init__(self, log, client, notifier_object):
        self.log = log
        self.client = client
        self.notifier = notifier_object

    def check_queue_conditions(self, arguments):
        response = self.client.get_queue()
        if response is None:
            return

        messages_ready = response.get("messages_ready")
        messages_unacknowledged = response.get("messages_unacknowledged")
        messages = response.get("messages")
        consumers = response.get("consumers")

        queue = arguments["server_queue"]
        queue_conditions = arguments["conditions"][queue]
        ready_size = queue_conditions.get("conditions_ready_queue_size")
        unack_size = queue_conditions.get("conditions_unack_queue_size")
        total_size = queue_conditions.get("conditions_total_queue_size")
        consumers_connected_min = queue_conditions.get("conditions_queue_consumers_connected")

        if ready_size is not None and messages_ready > ready_size:
            self.notifier.send_notification(f"{queue}: messages_ready = {messages_ready} > {ready_size}")

        if unack_size is not None and messages_unacknowledged > unack_size:
            self.notifier.send_notification(f"{queue}: messages_unacknowledged = {messages_unacknowledged} > {unack_size}")

        if total_size is not None and messages > total_size:
            self.notifier.send_notification(f"{queue}: messages = {messages} > {total_size}")

        if consumers_connected_min is not None and consumers < consumers_connected_min:
            self.notifier.send_notification(f"{queue}: consumers_connected = {consumers} < {consumers_connected_min}")

    def check_consumer_conditions(self, arguments):
        response = self.client.get_consumers()
        if response is None:
            return

        consumers_connected = len(response)
        consumers_connected_min = arguments["generic_conditions"].get("conditions_consumers_connected")

        if consumers_connected_min is not None and consumers_connected < consumers_connected_min:
            self.notifier.send_notification(f"consumers_connected = {consumers_connected} < {consumers_connected_min}")

    def check_connection_conditions(self, arguments):
        response = self.client.get_connections()
        if response is None:
            return

        open_connections = len(response)
        open_connections_min = arguments["generic_conditions"].get("conditions_open_connections")

        if open_connections_min is not None and open_connections < open_connections_min:
            self.notifier.send_notification(f"open_connections = {open_connections} < {open_connections_min}")

    def check_node_conditions(self, arguments):
        response = self.client.get_nodes()
        if response is None:
            return

        nodes_running = len(response)
        conditions = arguments["generic_conditions"]
        nodes_run = conditions.get("conditions_nodes_running")
        node_memory = conditions.get("conditions_node_memory_used")

        if nodes_run is not None and nodes_running < nodes_run:
            self.notifier.send_notification(f"nodes_running = {nodes_running} < {nodes_run}")

        for node in response:
            if node_memory is not None and node.get("mem_used") > (node_memory * 1024 ** 2):
                self.notifier.send_notification(f"Node {node.get('name')} - node_memory_used = {node.get('mem_used')} > {node_memory} MBs")
