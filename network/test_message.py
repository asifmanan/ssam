from network.message import Message

control_message = Message(content_type="CONTROL", content={
                            "action": "START",
                            "shard": "SomeShard",
                            "epoch": 1
                        }, sender="some_node")

msg = control_message.to_dict()

received_message = Message.from_dict(msg)
print(received_message.get_content())