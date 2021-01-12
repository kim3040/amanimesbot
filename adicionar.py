import sqlite3

def addaobanco(id,anime,assistidoem,episodioassistido):
 conn = sqlite3.connect("animes.db")
 cursor = conn.cursor()
 cursor.execute(f"""
SELECT * FROM infousers WHERE episodioassistido = {episodioassistido} AND anime = '{anime}'""")
 a = cursor.fetchall()
 if len(a) == 0:
  print("nao encontramos bb")
  conn.execute("""
 INSERT INTO infousers(id,anime,assistidoem,episodioassistido)
 VALUES(?,?,?,?)
 """,(id,anime,assistidoem,episodioassistido))
  conn.commit()
 else:
  print("nao encontrado")

addaobanco(20,"WINX","2020",20000)
