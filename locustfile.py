from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):

    def on_start(self):
        response = self.client.post("/account-api/login/", json={
            "username": "majid",
            "phone_number": "09177293982",
            "password": "Ms2420879422"
        })
        self.token = response.json().get("token")

    @task
    def list_stores(self):
        self.client.get("/finance-api/stores/", headers={"Authorization": f"Token {self.token}"})

    @task
    def create_credit_request(self):
        self.client.post("/finance-api/credit-request/", json={
            "amount": "1000000.000"
        }, headers={"Authorization": f"Token {self.token}"})

    @task
    def charge_customer(self):
        self.client.post("/finance-api/charge/", json={
            "phone_number": "09177293981",
            "amount": "5.000"
        }, headers={"Authorization": f"Token {self.token}"})


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
