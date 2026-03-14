def greet(name):
    return f"Hey {name}, du bist auf dem Weg zum DevOps Engineer!"

def create_bucket_name(project, env="dev"):
    return f"{project}-{env}-bucket"

def get_instance_info():
    name = "nouaim-webserver-01"
    status = "stopped"
    return name, status  # gibt zwei Werte zurück!

print(greet("Nouaim"))

print(create_bucket_name("devops-journey"))
print(create_bucket_name("devops-journey", "prod"))

instance_name, instance_status = get_instance_info()
print(f"{instance_name} ist {instance_status}")