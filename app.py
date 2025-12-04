from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from db_control import crud, mymodels_MySQL #db_controlディレクトリ内のcrud.pyとmymodells.pyをimportしている

# MySQLのテーブル作成
from db_control.create_tables_MySQL import init_db

# アプリケーション初期化時にテーブルを作成
init_db()


# Pydanticモデル定義（APIで受け取るJsonデータの型指定）
class Customer(BaseModel): # mymodelsから持ってきている
    customer_id: str
    customer_name: str
    age: int
    gender: str


app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # すべてのオリジンを許可している
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE　全許可
    allow_headers=["*"], 
)


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.post("/customers")
def create_customer(customer: Customer): #顧客を追加
    values = customer.dict()
    tmp = crud.myinsert(mymodels_MySQL.Customers, values) # 追加処理
    result = crud.myselect(mymodels_MySQL.Customers, values.get("customer_id")) # 登録内容を再取得

    if result:
        result_obj = json.loads(result)
        return result_obj if result_obj else None # もしなければNoneを返す
    return None


@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    result = crud.myselect(mymodels_MySQL.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found") #エラーハンドリング
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels_MySQL.Customers)
    # 結果がNoneの場合は空配列を返す
    if not result:
        return []
    # JSON文字列をPythonオブジェクトに変換
    return json.loads(result)


@app.put("/customers")
def update_customer(customer: Customer):
    values = customer.dict()
    values_original = values.copy()
    tmp = crud.myupdate(mymodels_MySQL.Customers, values) # 更新実行
    result = crud.myselect(mymodels_MySQL.Customers, values_original.get("customer_id")) # 更新後データ取得
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    result = crud.mydelete(mymodels_MySQL.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}


@app.get("/fetchtest") # 外部API呼び出しテスト（通信確認用？）
def fetchtest():
    response = requests.get('https://jsonplaceholder.typicode.com/users')
    return response.json()
