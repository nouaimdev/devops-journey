services = ["EC2", "S3", "RDS", "Lambda", "VPC"]

print(services[0])   # erstes Element
print(services[-1])  # letztes Element

for service in services:
    print(f"  - {service}")

# Dictionary (kennst du aus PHP als associative array)
ec2_instance = {
    "name": "nouaim-webserver-01",
    "type": "t3.micro",
    "status": "stopped"
}

for key, value in ec2_instance.items():
    print(f"  {key}: {value}")