# ---Librerias --- #

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import locale
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import os
import sys




# ******************** FUNCIÓN PARA RUTAS COMPATIBLES ******************** #
def obtener_ruta(ruta_relativa):
    """ 
    Permite encontrar los archivos (Iconos, Imágenes) tanto en modo desarrollo 
    como cuando el programa se convierte en un ejecutable (.exe).
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)




# ******************** CONFIGURACIÓN DE IDIOMA ******************** #
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
        except:
            pass 




# ******************** CONFIGURACION DE COLORES DEL SESTEMA ******************** #
COLOR_BG = "#000000"
COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#3498db"
COLOR_DANGER = "#e74c3c"
COLOR_SUCCESS = "#27ae60"
COLOR_LIGHT = "#f8f9fa"
COLOR_SKY_BLUE = "#87CEEB" 




# ******************** CLASS FINANZAS PRO ******************** #
class FinanzasPro:
    def __init__(self, root, usuario_id, nombre_usuario):
        self.root = root
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario
        
        self.root.title(f"Sistema De Control - Usuario: {self.nombre_usuario}")
        self.root.geometry("1200x700")
        self.root.configure(bg=COLOR_BG)
        self.root.state('zoomed')
        
        # Ruta del icono corregida para compatibilidad
        try:
            self.root.iconbitmap(obtener_ruta("Iconos/hacker.ico"))
        except:
            pass

        self.conn = sqlite3.connect("control_gastos.db")
        self.cursor = self.conn.cursor()
        
        try:
            self.cursor.execute("ALTER TABLE usuarios ADD COLUMN imagen_fondo TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE usuarios ADD COLUMN ruta_pdf TEXT")
        except: pass
        self.conn.commit()

        self.meses_dict = {
            "Todos": 0, 
            "Enero": 1, 
            "Febrero": 2, 
            "Marzo": 3, 
            "Abril": 4, 
            "Mayo": 5, 
            "Junio": 6, 
            "Julio": 7, 
            "Agosto": 8, 
            "Septiembre": 9, 
            "Octubre": 10, 
            "Noviembre": 11, 
            "Diciembre": 12
        }

        self.Dia = ["Lunes", 
                    "Martes", 
                    "Miercoles", 
                    "Jueves", 
                    "Viernes", 
                    "Sabado", 
                    "Domingo"
                    ]

        self.style_config()
        self.create_widgets()

        self.setup_tab_inicio()
        self.setup_tab_registros()
        self.setup_tab_graficos()
        self.setup_tab_exportar()
        self.setup_tab_configuracion() 
        self.setup_tab_agradecimiento()
        self.setup_tab_manual()
        self.setup_tab_informacion()
        self.setup_tab_creador()         
        self.actualizar_anios_disponibles()
        self.actualizar_tabla()

    def style_config(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[10, 5], font=('Segoe UI', 9, 'bold'))
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), 
                        background=COLOR_PRIMARY, foreground="white")
        style.map("Treeview", foreground=[('selected', 'white')], background=[('selected', COLOR_ACCENT)])

    def create_widgets(self):
        header = tk.Frame(self.root, bg=COLOR_PRIMARY, height=70)
        header.pack(fill="x")
        
        tk.Label(header, text=f"CONTROL DE {self.nombre_usuario.upper()}", 
                 font=("Segoe UI", 16, "bold"), bg=COLOR_PRIMARY, fg="white").pack(side="left", padx=20, pady=15)

        btn_salir = tk.Button(header, text="SALIR", bg=COLOR_DANGER, fg="white", 
                              font=("Segoe UI", 9, "bold"), command=self.salir_sistema, width=10)
        btn_salir.pack(side="right", padx=10, pady=15)

        btn_logout = tk.Button(header, text="CERRAR SESIÓN", bg=COLOR_ACCENT, fg="white", 
                               font=("Segoe UI", 9, "bold"), command=self.volver_login, width=15)
        btn_logout.pack(side="right", padx=10, pady=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_inicio = tk.Frame(self.notebook, bg="white")
        self.tab_registros = tk.Frame(self.notebook, bg="white")
        self.tab_graficos = tk.Frame(self.notebook, bg="white")
        self.tab_exportar = tk.Frame(self.notebook, bg="white")
        self.tab_configuracion = tk.Frame(self.notebook, bg="white") 
        self.tab_agradecimiento = tk.Frame(self.notebook, bg="white")
        self.tab_manual = tk.Frame(self.notebook, bg="white")
        self.tab_informacion = tk.Frame(self.notebook, bg="white")
        self.tab_creador = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab_inicio, text="INICIO")
        self.notebook.add(self.tab_registros, text="REGISTROS")
        self.notebook.add(self.tab_graficos, text="GRÁFICOS")
        self.notebook.add(self.tab_exportar, text="EXPORTAR")
        self.notebook.add(self.tab_configuracion, text="CONFIGURACION")
        self.notebook.add(self.tab_agradecimiento, text="AGRADECIMIENTO")
        self.notebook.add(self.tab_manual, text="MANUAL")
        self.notebook.add(self.tab_informacion, text="INFORMACIÓN")
        self.notebook.add(self.tab_creador, text="INFORMACIÓN DEL CREADOR")

    def volver_login(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Desea volver a la pantalla de acceso?"):
            self.conn.close()
            self.root.destroy()
            nueva_raiz = tk.Tk()
            LoginApp(nueva_raiz)
            nueva_raiz.mainloop()

    def salir_sistema(self):
        if messagebox.askyesno("Salir", "¿Está seguro que desea cerrar la aplicación?"):
            self.conn.close()
            self.root.quit()







# ******************** MODULO (PESTAÑA INICIO) ******************** #
    def setup_tab_inicio(self):
        self.canvas_inicio = tk.Canvas(self.tab_inicio, bg="white", highlightthickness=0)
        self.canvas_inicio.pack(fill="both", expand=True)
        
        self.cursor.execute("SELECT imagen_fondo FROM usuarios WHERE id = ?", (self.usuario_id,))
        res = self.cursor.fetchone()
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ruta_imagen_inicio = os.path.join(BASE_DIR, "Finanza 2025", "control de ingresos y egresos.jpg")
        
        if res and res[0]:
            if os.path.exists(res[0]):
                self.ruta_imagen_inicio = res[0]

        try:
            self.img_original = Image.open(self.ruta_imagen_inicio)
            self.canvas_inicio.bind("<Configure>", self.redimensionar_imagen_inicio)
        except Exception:
            tk.Label(self.canvas_inicio, text="Bienvenido al Sistema de Finanzas\n(Imagen no encontrada)", 
                     bg="white", font=("Segoe UI", 14)).pack(pady=100)

    def redimensionar_imagen_inicio(self, event):
        nuevo_ancho = event.width
        nuevo_alto = event.height
        if nuevo_ancho > 0 and nuevo_alto > 0:
            img_redimensionada = self.img_original.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img_redimensionada)
            self.canvas_inicio.delete("all")
            self.canvas_inicio.create_image(0, 0, anchor="nw", image=self.img_tk)





# ******************** MODULO (REGISTROS) ******************** #

    def setup_tab_registros(self):
        form_frame = tk.LabelFrame(self.tab_registros, text=" Nuevo Movimiento / Filtros ", bg="white", padx=15, pady=15)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(form_frame, text="Fecha (DD-MM-YYYY):", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_fecha = tk.Entry(form_frame, width=20)
        self.ent_fecha.insert(0, datetime.now().strftime("%d-%m-%Y"))
        self.ent_fecha.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Tipo:", bg="white").grid(row=0, column=2, sticky="w", pady=5)
        self.var_tipo = tk.StringVar(value="Ingreso")
        self.combo_tipo = ttk.Combobox(form_frame, textvariable=self.var_tipo, values=["Ingreso", "Egreso"], state="readonly", width=18)
        self.combo_tipo.grid(row=0, column=3, padx=10, pady=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", self.actualizar_categorias_principal)

        tk.Label(form_frame, text="Categoría:", bg="white").grid(row=0, column=4, sticky="w", pady=5)
        self.ent_categoria = ttk.Combobox(form_frame, state="readonly", width=25)
        self.ent_categoria.grid(row=0, column=5, padx=10, pady=5)
        
        tk.Label(form_frame, text="Monto (Bs.):", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        self.ent_monto = tk.Entry(form_frame, width=20)
        self.ent_monto.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(form_frame, text="Guardar Registro", command=self.guardar_datos, 
                  bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 10, "bold"), width=20).grid(row=1, column=2, columnspan=2, padx=10, sticky="w")

        tk.Label(form_frame, text="Filtrar por Mes:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.combo_mes = ttk.Combobox(form_frame, values=list(self.meses_dict.keys()), state="readonly", width=18)
        self.combo_mes.set("Todos")
        self.combo_mes.grid(row=2, column=1, padx=10, pady=5)
        self.combo_mes.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tabla())

        tk.Label(form_frame, text="Filtrar por Año:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=2, sticky="w", pady=5)
        self.combo_anio = ttk.Combobox(form_frame, state="readonly", width=18)
        self.combo_anio.grid(row=2, column=3, padx=10, pady=5)
        self.combo_anio.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tabla())

        self.lbl_total_ingresos = tk.Label(form_frame, text="Total Ingresos: 0,00 Bs.", bg="white", fg=COLOR_SUCCESS, font=("Segoe UI", 10, "bold"))
        self.lbl_total_ingresos.grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        # SE CAMBIA A COLOR ROJO (COLOR_DANGER)
        self.lbl_total_egresos = tk.Label(form_frame, text="Total Egresos: 0,00 Bs.", bg="white", fg=COLOR_DANGER, font=("Segoe UI", 10, "bold"))
        self.lbl_total_egresos.grid(row=3, column=2, columnspan=2, sticky="w", pady=10)

        self.lbl_total_neto = tk.Label(form_frame, text="Total Restante: 0,00 Bs.", bg="white", fg=COLOR_ACCENT, font=("Segoe UI", 10, "bold"))
        self.lbl_total_neto.grid(row=3, column=4, columnspan=2, sticky="w", pady=10)

        self.actualizar_categorias_principal()

        self.tree = ttk.Treeview(self.tab_registros, columns=("ID", "Dia", "Fecha", "Tipo", "Categoría", "Monto"), show='headings', height=15)
        
        # CONFIGURACIÓN DE COLORES Y NEGRITA PARA LA TABLA
        self.tree.tag_configure("egreso", foreground=COLOR_DANGER, font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure("ingreso", foreground="black", font=("Segoe UI", 10, "bold"))

        for col in [("ID", 50), ("Dia", 100), ("Fecha", 120), ("Tipo", 120), ("Categoría", 200), ("Monto", 150)]:
            self.tree.heading(col[0], text=col[0])
            self.tree.column(col[0], width=col[1], anchor="center" if col[0] != "Categoría" else "w")
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self.on_item_double_click)





# ******************** MODULO (GRAFICAS ACTUALIZADO CON HISTORIAL) ******************** #

    def setup_tab_graficos(self):
        filter_frame = tk.Frame(self.tab_graficos, bg="white", pady=10)
        filter_frame.pack(fill="x")

        tk.Label(filter_frame, text="Mes:", bg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        self.combo_mes_graf = ttk.Combobox(filter_frame, values=list(self.meses_dict.keys()), state="readonly", width=15)
        self.combo_mes_graf.set("Todos")
        self.combo_mes_graf.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Año:", bg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        self.combo_anio_graf = ttk.Combobox(filter_frame, state="readonly", width=10)
        self.combo_anio_graf.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Generar Análisis", command=self.generar_graficos, bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=20)

        self.chart_container = tk.Frame(self.tab_graficos, bg="white")
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=10)

    # Limpiar contenedor y generar gráficos
    def generar_graficos(self):
        for widget in self.chart_container.winfo_children(): 
            widget.destroy()

        mes = self.meses_dict[self.combo_mes_graf.get()]
        anio = self.combo_anio_graf.get()

        # Filtros de consulta SQL        
        filter_sql = " WHERE usuario_id = ?"
        params = [self.usuario_id]
        if mes != 0: filter_sql += " AND mes = ?"; params.append(mes)
        if anio != "Todos" and anio != "": filter_sql += " AND año = ?"; params.append(int(anio))

        # 1. Obtener Datos Generales para el Pie
        self.cursor.execute(f"SELECT tipo, SUM(monto) FROM movimientos {filter_sql} GROUP BY tipo", params)
        datos_generales = dict(self.cursor.fetchall())
        
        if not datos_generales:
            tk.Label(self.chart_container, text="No hay datos registrados para este periodo", bg="white", font=("Segoe UI", 12), fg=COLOR_DANGER).pack(expand=True)
            return
        
        # 2. Obtener Historial por Categoría (Ingresos)
        self.cursor.execute(f"SELECT categoria, SUM(monto) FROM movimientos {filter_sql} AND tipo='Ingreso' GROUP BY categoria ORDER BY SUM(monto) DESC", params)
        ingresos_cat = self.cursor.fetchall()

        # 3. Obtener Historial por Categoría (Egresos)
        self.cursor.execute(f"SELECT categoria, SUM(monto) FROM movimientos {filter_sql} AND tipo='Egreso' GROUP BY categoria ORDER BY SUM(monto) DESC", params)
        egresos_cat = self.cursor.fetchall()

        # --- ESTRUCTURA DE COLUMNAS ---
        col_izq = tk.Frame(self.chart_container, bg="white", padx=10)
        col_izq.pack(side="left", fill="both", expand=True)
        
        col_centro = tk.Frame(self.chart_container, bg="white")
        col_centro.pack(side="left", fill="both", expand=True)
        
        col_der = tk.Frame(self.chart_container, bg="white", padx=10)
        col_der.pack(side="left", fill="both", expand=True)

        # Renderizar Columna Izquierda (INGRESOS)
        tk.Label(col_izq, text="HISTORIAL INGRESOS", font=("Segoe UI", 11, "bold"), bg="white", fg=COLOR_SUCCESS).pack(pady=10)
        f_ing = tk.Frame(col_izq, bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#eee")
        f_ing.pack(fill="both", expand=True)
        for cat, monto in ingresos_cat:
            f_row = tk.Frame(f_ing, bg="#f9f9f9")
            f_row.pack(fill="x", padx=5, pady=2)
            tk.Label(f_row, text=cat, bg="#f9f9f9", font=("Segoe UI", 9)).pack(side="left")
            tk.Label(f_row, text=f"{self.format_bs(monto)} Bs.", bg="#f9f9f9", font=("Segoe UI", 9, "bold")).pack(side="right")

        # Renderizar Columna Centro (GRÁFICO)
        fig, ax = plt.subplots(figsize=(4, 4))
        labels = list(datos_generales.keys())
        valores = list(datos_generales.values())
        colores = [COLOR_SUCCESS if l == "Ingreso" else COLOR_DANGER for l in labels]
        ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90, colors=colores, wedgeprops={'edgecolor': 'white'})
        ax.set_title("Balance General")
        canvas = FigureCanvasTkAgg(fig, master=col_centro)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

        # Renderizar Columna Derecha (EGRESOS)
        tk.Label(col_der, text="HISTORIAL EGRESOS", font=("Segoe UI", 11, "bold"), bg="white", fg=COLOR_DANGER).pack(pady=10)
        f_egr = tk.Frame(col_der, bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#eee")
        f_egr.pack(fill="both", expand=True)
        for cat, monto in egresos_cat:
            f_row = tk.Frame(f_egr, bg="#f9f9f9")
            f_row.pack(fill="x", padx=5, pady=2)
            tk.Label(f_row, text=cat, bg="#f9f9f9", font=("Segoe UI", 9)).pack(side="left")
            tk.Label(f_row, text=f"{self.format_bs(monto)} Bs.", bg="#f9f9f9", font=("Segoe UI", 9, "bold")).pack(side="right")

    def format_bs(self, monto):
        return f"{monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # FUNCION ACTUALIZADA PARA USAR LA LISTA DE DIAS PERSONALIZADA
    def obtener_nombre_dia(self, fecha_str):
        try:
            fecha_dt = datetime.strptime(fecha_str, "%d-%m-%Y")
            # Usa el indice del dia (0=Lunes, 6=Domingo) para acceder a self.Dia
            return self.Dia[fecha_dt.weekday()]
        except:
            return "N/A"

    def actualizar_tabla(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        mes_sel = self.combo_mes.get()
        anio_sel = self.combo_anio.get()
        query = "SELECT id, fecha, tipo, categoria, monto FROM movimientos WHERE usuario_id = ?"
        params = [self.usuario_id]
        if mes_sel != "Todos":
            query += " AND mes = ?"; params.append(self.meses_dict[mes_sel])
        if anio_sel != "Todos":
            query += " AND año = ?"; params.append(int(anio_sel))
        query += " ORDER BY id DESC"
        self.cursor.execute(query, params)
        total_ing = total_egr = 0
        for row in self.cursor.fetchall():
            id_v, fec, tip, cat, mon = row
            dia_semana = self.obtener_nombre_dia(fec)
            if tip == "Ingreso": 
                total_ing += mon
                tag = "ingreso"
            else: 
                total_egr += mon
                tag = "egreso"
            
            # Se aplica el tag correspondiente para el color y negrita
            self.tree.insert("", "end", values=(id_v, dia_semana, fec, tip, cat, self.format_bs(mon)), tags=(tag,))
        
        restante = total_ing - total_egr
        self.lbl_total_ingresos.config(text=f"Total Ingresos: {self.format_bs(total_ing)} Bs.")
        self.lbl_total_egresos.config(text=f"Total Egresos: {self.format_bs(total_egr)} Bs.")
        self.lbl_total_neto.config(text=f"Total Restante: {self.format_bs(restante)} Bs.")

    def actualizar_anios_disponibles(self):
        self.cursor.execute("SELECT DISTINCT año FROM movimientos WHERE usuario_id = ? ORDER BY año DESC", (self.usuario_id,))
        anios = [str(row[0]) for row in self.cursor.fetchall()]
        opciones = ["Todos"] + (anios if anios else [str(datetime.now().year)])
        self.combo_anio['values'] = opciones
        self.combo_anio_graf['values'] = opciones
        self.combo_anio.set("Todos")
        self.combo_anio_graf.set("Todos")
        if hasattr(self, 'combo_anio_exp'):
            self.combo_anio_exp['values'] = opciones
            self.combo_anio_exp.set("Todos")

    def actualizar_categorias_principal(self, event=None):
        if self.var_tipo.get() == "Ingreso": lista = ["Sueldo", "Bonos", "Inversiones", "Regalo" ,"Otros Ingresos"]
        else: lista = ["Alimentos", "Transporte", "Servicios", "Wifi" ,"Gas" ,"CLAP" ,"Agua" ,"Salud", "Educación", "Ocio", "Otros Gastos"]
        self.ent_categoria['values'] = lista
        self.ent_categoria.set(lista[0])

    def guardar_datos(self):
        try:
            monto_texto = self.ent_monto.get().replace(".", "").replace(",", ".")
            monto = float(monto_texto)
            f_obj = datetime.strptime(self.ent_fecha.get(), "%d-%m-%Y")
            self.cursor.execute("""INSERT INTO movimientos (fecha, año, mes, categoria, monto, tipo, usuario_id) 
                                VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                                (self.ent_fecha.get(), f_obj.year, f_obj.month, self.ent_categoria.get(), monto, self.var_tipo.get(), self.usuario_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro guardado")
            self.ent_monto.delete(0, tk.END); self.actualizar_tabla(); self.actualizar_anios_disponibles()
        except Exception: messagebox.showerror("Error", "Verifique el monto y la fecha (DD-MM-YYYY)")

    def on_item_double_click(self, event):
        try:
            item_id = self.tree.selection()[0]
            valores = self.tree.item(item_id, 'values')
            edit_win = tk.Toplevel(self.root); edit_win.title("Editar / Eliminar Registro"); edit_win.geometry("350x450"); edit_win.configure(bg="white"); edit_win.grab_set()
            tk.Label(edit_win, text=f"Editando Registro ID: {valores[0]}", font=("Segoe UI", 11, "bold"), bg="white").pack(pady=10)
            tk.Label(edit_win, text="Fecha (DD-MM-YYYY):", bg="white").pack()
            ent_f = tk.Entry(edit_win); ent_f.insert(0, valores[2]); ent_f.pack(pady=5)
            tk.Label(edit_win, text="Tipo:", bg="white").pack()
            cmb_t = ttk.Combobox(edit_win, values=["Ingreso", "Egreso"], state="readonly"); cmb_t.set(valores[3]); cmb_t.pack(pady=5)
            tk.Label(edit_win, text="Categoría:", bg="white").pack()
            ent_c = tk.Entry(edit_win); ent_c.insert(0, valores[4]); ent_c.pack(pady=5)
            tk.Label(edit_win, text="Monto (Bs):", bg="white").pack()
            ent_m = tk.Entry(edit_win); ent_m.insert(0, valores[5]); ent_m.pack(pady=5)
            btn_frame = tk.Frame(edit_win, bg="white"); btn_frame.pack(pady=20)
            tk.Button(btn_frame, text="Actualizar", bg=COLOR_SUCCESS, fg="white", width=12, command=lambda: self.actualizar_registro(valores[0], ent_f.get(), cmb_t.get(), ent_c.get(), ent_m.get(), edit_win)).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar", bg=COLOR_DANGER, fg="white", width=12, command=lambda: self.confirmar_eliminacion(valores[0], edit_win)).pack(side="left", padx=5)
        except IndexError: pass

    def actualizar_registro(self, id_reg, fecha, tipo, cat, monto_str, ventana):
        try:
            monto = float(monto_str.replace(".", "").replace(",", "."))
            f_obj = datetime.strptime(fecha, "%d-%m-%Y")
            self.cursor.execute("""UPDATE movimientos SET fecha=?, año=?, mes=?, categoria=?, monto=?, tipo=? WHERE id=?""", (fecha, f_obj.year, f_obj.month, cat, monto, tipo, id_reg))
            self.conn.commit(); messagebox.showinfo("Éxito", "Registro actualizado"); ventana.destroy(); self.actualizar_tabla()
        except Exception: messagebox.showerror("Error", "Datos inválidos. Verifique fecha y monto.")

    def confirmar_eliminacion(self, id_reg, ventana):
        if messagebox.askyesno("Confirmar", "¿Desea eliminar este registro definitivamente?"):
            self.cursor.execute("DELETE FROM movimientos WHERE id=?", (id_reg,))
            self.conn.commit(); ventana.destroy(); self.actualizar_tabla(); self.actualizar_anios_disponibles()





# ******************** MODULO (EXPORTAR PDF) ******************** #
    def setup_tab_exportar(self):
        container = tk.Frame(self.tab_exportar, bg="white", padx=50, pady=50)
        container.pack(expand=True)
        tk.Label(container, text="EXPORTAR REPORTES PDF", font=("Segoe UI", 14, "bold"), bg="white", fg=COLOR_PRIMARY).pack(pady=20)
        tk.Label(container, text="Filtrar por Mes:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=5)
        self.combo_mes_exp = ttk.Combobox(container, values=list(self.meses_dict.keys()), state="readonly", width=30); self.combo_mes_exp.set("Todos"); self.combo_mes_exp.pack(pady=5)
        tk.Label(container, text="Filtrar por Año:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=5)
        self.combo_anio_exp = ttk.Combobox(container, state="readonly", width=30); self.combo_anio_exp.pack(pady=5)
        btn_exp = tk.Button(container, text="GENERAR PDF", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 11, "bold"), width=25, command=self.exportar_pdf); btn_exp.pack(pady=30)

    def exportar_pdf(self):
        mes_nombre = self.combo_mes_exp.get(); mes_num = self.meses_dict[mes_nombre]; anio = self.combo_anio_exp.get()
        query = "SELECT fecha, tipo, categoria, monto FROM movimientos WHERE usuario_id = ?"
        params = [self.usuario_id]
        if mes_num != 0: query += " AND mes = ?"; params.append(mes_num)
        if anio != "Todos" and anio != "": query += " AND año = ?"; params.append(int(anio))
        query += " ORDER BY id DESC"
        self.cursor.execute(query, params); datos = self.cursor.fetchall()
        
        if not datos: messagebox.showwarning("Sin datos", "No hay registros para el periodo seleccionado"); return
        
        self.cursor.execute("SELECT ruta_pdf FROM usuarios WHERE id = ?", (self.usuario_id,))
        res_ruta = self.cursor.fetchone()
        ruta_base = res_ruta[0] if res_ruta and res_ruta[0] else os.getcwd()

        try:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, f"Reporte de Finanzas - {self.nombre_usuario}", ln=True, align='C')
            pdf.set_font("Arial", '', 10); pdf.cell(0, 10, f"Periodo: {mes_nombre} / {anio} - Generado el: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
            pdf.ln(10); pdf.set_fill_color(44, 62, 80); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 10)
            pdf.cell(30, 8, "Fecha", 1, 0, 'C', True); pdf.cell(30, 8, "Tipo", 1, 0, 'C', True); pdf.cell(80, 8, "Categoría", 1, 0, 'C', True); pdf.cell(50, 8, "Monto (Bs)", 1, 1, 'C', True)
            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9); total_ing = total_egr = 0
            for f, t, c, m in datos:
                if t == "Ingreso": total_ing += m
                else: total_egr += m
                pdf.cell(30, 7, f, 1, 0, 'C'); pdf.cell(30, 7, t, 1, 0, 'C'); pdf.cell(80, 7, c[:40], 1, 0, 'L'); pdf.cell(50, 7, self.format_bs(m), 1, 1, 'R')
            pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, f"TOTAL INGRESOS: {self.format_bs(total_ing)} Bs.", ln=True, align='R'); pdf.cell(0, 7, f"TOTAL EGRESOS: {self.format_bs(total_egr)} Bs.", ln=True, align='R'); pdf.cell(0, 7, f"BALANCE NETO: {self.format_bs(total_ing - total_egr)} Bs.", ln=True, align='R')
            
            nombre_archivo = f"Reporte_{self.nombre_usuario}_{mes_nombre}_{anio}.pdf"
            ruta_completa = os.path.join(ruta_base, nombre_archivo)
            pdf.output(ruta_completa); messagebox.showinfo("Éxito", f"PDF generado en: {ruta_completa}")
        except Exception as e: messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")




# ******************** MODULO (CONFIGURACION) ******************** #

    def setup_tab_configuracion(self):
        for widget in self.tab_configuracion.winfo_children(): widget.destroy()
        
        self.tab_configuracion.configure(bg=COLOR_LIGHT)
        
        main_scroll = tk.Canvas(self.tab_configuracion, bg=COLOR_LIGHT, highlightthickness=0)
        v_scroll = ttk.Scrollbar(self.tab_configuracion, orient="vertical", command=main_scroll.yview)
        scroll_frame = tk.Frame(main_scroll, bg=COLOR_LIGHT)
        
        scroll_frame.bind("<Configure>", lambda e: main_scroll.configure(scrollregion=main_scroll.bbox("all")))
        main_scroll.create_window((0, 0), window=scroll_frame, anchor="nw", width=self.root.winfo_screenwidth())
        main_scroll.configure(yscrollcommand=v_scroll.set)
        
        main_scroll.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        header_cfg = tk.Frame(scroll_frame, bg=COLOR_PRIMARY, pady=20)
        header_cfg.pack(fill="x")
        tk.Label(header_cfg, text="PANEL DE CONFIGURACIÓN Y PERSONALIZACIÓN", font=("Segoe UI", 16, "bold"), fg="white", bg=COLOR_PRIMARY).pack()

        content_cfg = tk.Frame(scroll_frame, bg=COLOR_LIGHT, padx=40, pady=20)
        content_cfg.pack(fill="both", expand=True)

        card1 = tk.LabelFrame(content_cfg, text=" Aspecto Visual ", font=("Segoe UI", 11, "bold"), bg="white", padx=20, pady=15, relief="flat", highlightthickness=1, highlightbackground="#ddd")
        card1.pack(fill="x", pady=10)
        
        tk.Label(card1, text="Imagen de fondo para la pestaña Inicio:", bg="white", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.cursor.execute("SELECT imagen_fondo FROM usuarios WHERE id = ?", (self.usuario_id,))
        res_img = self.cursor.fetchone()
        ruta_img = res_img[0] if res_img and res_img[0] else "No seleccionada"

        f_img = tk.Frame(card1, bg="white")
        f_img.pack(fill="x", pady=10)
        self.ent_img_path = tk.Entry(f_img, font=("Segoe UI", 10), bg=COLOR_LIGHT, relief="flat", highlightthickness=1)
        self.ent_img_path.insert(0, ruta_img)
        self.ent_img_path.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        
        tk.Button(f_img, text="Examinar", bg=COLOR_PRIMARY, fg="white", command=self.seleccionar_imagen, relief="flat", padx=15).pack(side="left", padx=5)
        tk.Button(f_img, text="Guardar Imagen", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 9, "bold"), command=self.actualizar_imagen_fondo, relief="flat", padx=15).pack(side="left")

        card2 = tk.LabelFrame(content_cfg, text="Almacenamiento de Reportes ", font=("Segoe UI", 11, "bold"), bg="white", padx=20, pady=15, relief="flat", highlightthickness=1, highlightbackground="#ddd")
        card2.pack(fill="x", pady=10)
        
        tk.Label(card2, text="Carpeta donde se guardarán los PDFs exportados:", bg="white", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.cursor.execute("SELECT ruta_pdf FROM usuarios WHERE id = ?", (self.usuario_id,))
        res_pdf = self.cursor.fetchone()
        ruta_pdf_val = res_pdf[0] if res_pdf and res_pdf[0] else os.getcwd()

        f_pdf = tk.Frame(card2, bg="white")
        f_pdf.pack(fill="x", pady=10)
        self.ent_pdf_path = tk.Entry(f_pdf, font=("Segoe UI", 10), bg=COLOR_LIGHT, relief="flat", highlightthickness=1)
        self.ent_pdf_path.insert(0, ruta_pdf_val)
        self.ent_pdf_path.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        
        tk.Button(f_pdf, text="Cambiar Carpeta", bg=COLOR_PRIMARY, fg="white", command=self.seleccionar_ruta_pdf, relief="flat", padx=15).pack(side="left", padx=5)
        tk.Button(f_pdf, text="Fijar Ruta", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 9, "bold"), command=self.actualizar_ruta_pdf, relief="flat", padx=15).pack(side="left")

        card3 = tk.LabelFrame(content_cfg, text="Seguridad de la Cuenta ", font=("Segoe UI", 11, "bold"), bg="white", padx=20, pady=15, relief="flat", highlightthickness=1, highlightbackground="#ddd")
        card3.pack(fill="x", pady=10)
        
        f_pass = tk.Frame(card3, bg="white")
        f_pass.pack(fill="x")
        
        tk.Label(f_pass, text="Nueva Contraseña:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_new_pass = tk.Entry(f_pass, show="*", font=("Segoe UI", 11), bg=COLOR_LIGHT, relief="flat", highlightthickness=1)
        self.ent_new_pass.grid(row=0, column=1, padx=10, sticky="ew", ipady=3)
        
        tk.Label(f_pass, text="Confirmar:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_conf_pass = tk.Entry(f_pass, show="*", font=("Segoe UI", 11), bg=COLOR_LIGHT, relief="flat", highlightthickness=1)
        self.ent_conf_pass.grid(row=1, column=1, padx=10, sticky="ew", ipady=3)
        
        tk.Button(card3, text="Actualizar Contraseña", bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 10, "bold"), command=self.cambiar_password, relief="flat", pady=7).pack(pady=15, fill="x")

        card4 = tk.LabelFrame(content_cfg, text="Gestión de Datos ", font=("Segoe UI", 11, "bold"), bg="white", padx=20, pady=15, relief="flat", highlightthickness=1, highlightbackground="#ddd")
        card4.pack(fill="x", pady=10)
        
        tk.Label(card4, text="Borrar historial completo de movimientos (Irreversible):", bg="white").pack(side="left")
        tk.Button(card4, text="ELIMINAR TODO", bg=COLOR_DANGER, fg="white", font=("Segoe UI", 9, "bold"), command=self.borrar_todos_datos, relief="flat", padx=20).pack(side="right")

    def seleccionar_ruta_pdf(self):
        directorio = filedialog.askdirectory(title="Seleccionar Carpeta para Reportes")
        if directorio:
            self.ent_pdf_path.delete(0, tk.END)
            self.ent_pdf_path.insert(0, directorio)

    def actualizar_ruta_pdf(self):
        nueva_ruta = self.ent_pdf_path.get()
        if not os.path.isdir(nueva_ruta):
            messagebox.showerror("Error", "La ruta seleccionada no es válida.")
            return
        try:
            self.cursor.execute("UPDATE usuarios SET ruta_pdf = ? WHERE id = ?", (nueva_ruta, self.usuario_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Ruta de exportación actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la ruta: {e}")

    def seleccionar_imagen(self):
        archivo = filedialog.askopenfilename(title="Seleccionar Imagen", 
                                            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp")])
        if archivo:
            self.ent_img_path.delete(0, tk.END)
            self.ent_img_path.insert(0, archivo)

    def actualizar_imagen_fondo(self):
        nueva_ruta = self.ent_img_path.get()
        if not nueva_ruta or not os.path.exists(nueva_ruta):
            messagebox.showerror("Error", "La ruta de la imagen no es válida.")
            return
        try:
            self.cursor.execute("UPDATE usuarios SET imagen_fondo = ? WHERE id = ?", (nueva_ruta, self.usuario_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Imagen de inicio actualizada. Los cambios se verán al reiniciar la pestaña Inicio.")
            self.setup_tab_inicio()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")

    def cambiar_password(self):
        p1, p2 = self.ent_new_pass.get(), self.ent_conf_pass.get()
        if not p1 or p1 != p2: messagebox.showerror("Error", "Las contraseñas no coinciden o están vacías"); return
        if messagebox.askyesno("Confirmar", "¿Seguro que desea cambiar su contraseña?"):
            self.cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (p1, self.usuario_id))
            self.conn.commit(); messagebox.showinfo("Éxito", "Contraseña actualizada correctamente"); self.ent_new_pass.delete(0, tk.END); self.ent_conf_pass.delete(0, tk.END)

    def borrar_todos_datos(self):
        if messagebox.askyesno("¡ADVERTENCIA!", "¿Está TOTALMENTE SEGURO de eliminar todos sus movimientos?\nEsta acción no se puede deshacer."):
            self.cursor.execute("DELETE FROM movimientos WHERE usuario_id = ?", (self.usuario_id,))
            self.conn.commit(); messagebox.showinfo("Limpieza", "Se han eliminado todos sus registros."); self.actualizar_tabla()





# ******************** MODULO (AGRADECIMIENTO) ******************** #

    def setup_tab_agradecimiento(self):
        
        for widget in self.tab_agradecimiento.winfo_children(): widget.destroy()
        container = tk.Frame(self.tab_agradecimiento, bg="white")
        container.pack(expand=True, fill="both")
        
        main_frame = tk.Frame(container, bg="white", relief="groove", bd=2, padx=40, pady=40)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(main_frame, text="¡GRACIAS POR USAR MI SISTEMA!", font=("Segoe UI", 18, "bold"), bg="white", fg=COLOR_ACCENT).pack(pady=(0, 20))
        
        texto_agradecimiento = (f"Estimado(a) {self.nombre_usuario},\n\n"
            "Es un honor para mí que hayas elegido esta plataforma para tomar las riendas de tu futuro financiero. "
            "Finanzas Pro ha sido meticulosamente desarrollado para transformar la complejidad de tus cuentas diarias "
            "en claridad estratégica y control total.\n\n"
            "Mi objetivo es que esta herramienta sea el aliado clave que te impulse a alcanzar tus metas de ahorro e "
            "inversión, fomentando una economía personal saludable y organizada.\n\n"
            "¡Gracias por ser parte de esta experiencia y confiar en la excelencia tecnológica!")
        
        tk.Label(main_frame, text=texto_agradecimiento, font=("Segoe UI", 11), bg="white", justify="center", wraplength=500).pack(pady=10)
        
        tk.Label(main_frame, text="Versión 2.0 - 2025", font=("Segoe UI", 9, "italic"), bg="white", fg="gray").pack(pady=20)
        
        tk.Button(main_frame, text="Continuar Administrando", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), width=25, command=lambda: self.notebook.select(self.tab_inicio)).pack(pady=10)




# ******************** MODULO (PESTAÑA MANUAL E INFORMACION TECNICA) ******************** #
    
    def setup_tab_manual(self):
        
        for widget in self.tab_manual.winfo_children(): widget.destroy()
        container = tk.Frame(self.tab_manual, bg="white")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        tk.Label(container, text="MANUAL DE USUARIO COMPLETO", font=("Segoe UI", 16, "bold"), bg="white", fg=COLOR_PRIMARY).pack(pady=(0, 15))
        
        text_frame = tk.Frame(container, bg="white")
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        txt_manual = tk.Text(text_frame, font=("Segoe UI", 11), wrap="word", padx=20, pady=20, yscrollcommand=scrollbar.set, bg="#f4f7f6", fg="#2c3e50")
        txt_manual.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=txt_manual.yview)
        
        manual_contenido = """
SISTEMA FINANZAS PRO v2.5 - GUÍA COMPLETA DE USUARIO
----------------------------------------------------------------------------------------------------
Bienvenido al panel de control de su economía personal. Este software ha sido diseñado para 
ofrecerle una visión clara y estratégica de sus flujos monetarios.

1. GESTIÓN DE REGISTROS (Módulo Principal)
   • Registro de Datos: Ingrese la fecha (DD-MM-YYYY), seleccione el tipo de movimiento y la 
     categoría correspondiente. Ingrese el monto en Bolívares (Bs.).
     
   • Visualización Inteligente: La tabla de registros diferencia automáticamente sus finanzas:
     - Los INGRESOS se muestran en NEGRO para una lectura clara.
     - Los EGRESOS se muestran en ROJO resaltado (Negrita) para su inmediata identificación.
     
   • Edición y Borrado: Haga DOBLE CLIC sobre cualquier fila de la tabla para abrir la ventana 
     emergente de edición, donde podrá actualizar los datos o eliminar el registro permanentemente.
     
   • Filtros Dinámicos: Utilice los selectores de "Mes" y "Año" para segmentar su información. 
     Los totales de Ingresos, Egresos y Saldo Restante se actualizarán en tiempo real.

2. ANÁLISIS MEDIANTE GRÁFICOS
   • Balance General: Visualice un gráfico de pastel central con el porcentaje de distribución 
     entre sus entradas y salidas.
     
   • Historial Categorizado: 
     - COLUMNA IZQUIERDA: Desglose totalizado de Ingresos por categoría.
     - COLUMNA DERECHA: Desglose totalizado de Egresos por categoría.
     
   • Generación: Seleccione el periodo deseado y presione "Generar Análisis" para actualizar.

3. EXPORTACIÓN DE REPORTES (PDF)
   • Cree documentos profesionales de sus finanzas. Filtre por mes o año y el sistema generará 
     un archivo PDF con membrete, tabla detallada de movimientos y balance final.
     
   • Los archivos se guardarán automáticamente en la ruta establecida en "Configuración".

4. PANEL DE CONFIGURACIÓN Y PERSONALIZACIÓN
   • Seguridad: Actualice su contraseña de acceso en cualquier momento.
   
   • Identidad Visual: Personalice la pantalla de inicio cargando su propia imagen de fondo.
   
   • Rutas de Guardado: Cambie la carpeta predeterminada donde se descargan sus reportes PDF.
   
   • Mantenimiento: El botón "ELIMINAR TODO" permite resetear su historial de movimientos 
     (Use esta opción con precaución, ya que es irreversible).

5. ACCESO Y SEGURIDAD
   • El sistema cuenta con un módulo de login seguro. Si olvida su clave, utilice la opción 
     "Recuperar Clave" desde la pantalla de acceso inicial.
----------------------------------------------------------------------------------------------------
© 2025 - Desarrollo y Soporte: op2020pk@gmail.com
Ubicación: Venezuela
        """
        txt_manual.insert("1.0", manual_contenido)
        txt_manual.config(state="disabled")





# ******************** MODULO (PESTAÑA INFORMACION TECNICA) ******************** #
    
    def setup_tab_informacion(self):
        # Limpieza de la pestaña antes de renderizar
        for widget in self.tab_informacion.winfo_children(): 
            widget.destroy()
            
        container = tk.Frame(self.tab_informacion, bg="white", padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        # --- ENCABEZADO PROFESIONAL ---
        header_frame = tk.Frame(container, bg="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="ESPECIFICACIONES DEL ENTORNO", 
                 font=("Segoe UI", 18, "bold"), bg="white", fg=COLOR_PRIMARY).pack(side="left")
        
        # --- TARJETA DE DETALLES TÉCNICOS ---
        detalles_frame = tk.LabelFrame(container, text=" Configuración de Arquitectura ", 
                                      bg="white", font=("Segoe UI", 10, "bold"), padx=25, pady=25,
                                      relief="flat", highlightthickness=1, highlightbackground="#dee2e6")
        detalles_frame.pack(fill="x", pady=10)
        
        # Información precisa extraída del sistema
        info_tecnica = [
            ("🔹 Nombre del Software:", "Finanzas Pro v2.5"),
            ("🔹 Build de Compilación:", "2025.01.REVE"),
            ("🔹 Motor de Ejecución:", "Python 3.x con Tkinter GUI"),
            ("🔹 Base de Datos:", "SQLite3 (Relacional Local)"),
            ("🔹 Archivo Interno:", "control_gastos.db"),
            ("🔹 Análisis Gráfico:", "Matplotlib Engine"),
            ("🔹 Generador PDF:", "FPDF Library v1.7.2"),
            ("🔹 Renderizado:", "Pillow (PIL) Image Processing")
        ]
        
        for i, (label, value) in enumerate(info_tecnica):
            # Etiquetas de parámetros
            tk.Label(detalles_frame, text=label, font=("Segoe UI", 10, "bold"), 
                     bg="white", fg="#495057").grid(row=i, column=0, sticky="w", pady=5)
            # Valores de los parámetros
            tk.Label(detalles_frame, text=value, font=("Segoe UI", 10), 
                     bg="white", fg=COLOR_ACCENT).grid(row=i, column=1, sticky="w", padx=20, pady=5)
        
        # --- PANEL DE ESTADO Y SEGURIDAD ---
        # Verificación dinámica del estado de conexión
        status_frame = tk.Frame(container, bg="#f8f9fa", padx=20, pady=15, 
                               highlightthickness=1, highlightbackground="#e9ecef")
        status_frame.pack(fill="x", pady=20)
        
        # Indicador visual de conexión
        db_text = "NÚCLEO ACTIVO" if self.conn else "ERROR DE NÚCLEO"
        db_color = COLOR_SUCCESS if self.conn else COLOR_DANGER
        
        # Lado izquierdo: Estado de base de datos
        tk.Label(status_frame, text="Conexión de Datos:", 
                 font=("Segoe UI", 10, "bold"), bg="#f8f9fa").pack(side="left")
        
        lbl_status = tk.Label(status_frame, text=f" {db_text} ", 
                             font=("Segoe UI", 8, "bold"), bg=db_color, fg="white", 
                             padx=10, pady=2)
        lbl_status.pack(side="left", padx=15)
        
        # Lado derecho: Información de sesión
        tk.Label(status_frame, text=f"Sesión: {self.nombre_usuario.upper()}", 
                 font=("Segoe UI", 9, "italic"), bg="#f8f9fa", fg="#6c757d").pack(side="right")

        # --- PIE DE PÁGINA ---
        tk.Label(container, text="Este sistema utiliza cifrado local para la protección de movimientos financieros.", 
                 font=("Segoe UI", 8), bg="white", fg="gray").pack(side="bottom", pady=10)



# ******************** MODULO (PESTAÑA INFORMACION DEL CREADOR) ******************** #

    def setup_tab_creador(self):
        # Limpiar la pestaña antes de dibujar
        for widget in self.tab_creador.winfo_children():
            widget.destroy()
        
        # Contenedor principal con scroll (opcional) o fondo limpio
        container = tk.Frame(self.tab_creador, bg="#ffffff")
        container.pack(fill="both", expand=True)

        # Encabezado Elegante
        header_frame = tk.Frame(container, bg=COLOR_PRIMARY, pady=30)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="PERFIL DEL DESARROLLADOR", 
                 font=("Segoe UI", 20, "bold"), fg="white", bg=COLOR_PRIMARY).pack()
        tk.Label(header_frame, text="Soluciones Tecnológicas & Arquitectura de Software", 
                 font=("Segoe UI", 10), fg=COLOR_SKY_BLUE, bg=COLOR_PRIMARY).pack()

        # Cuerpo de la información
        body_frame = tk.Frame(container, bg="white", padx=60, pady=30)
        body_frame.pack(fill="both", expand=True)

        # --- SECCIÓN: BIOGRAFÍA ---
        bio_card = tk.LabelFrame(body_frame, text=" Trayectoria Profesional ", font=("Segoe UI", 11, "bold"),
                                 bg="white", padx=20, pady=20, fg=COLOR_PRIMARY, relief="flat", 
                                 highlightthickness=1, highlightbackground="#e0e0e0")
        bio_card.pack(fill="x", pady=(0, 20))

        bio_texto = (
            "Especialista en desarrollo de sistemas de escritorio con un enfoque en la optimización "
            "de procesos financieros y administrativos. Finanzas Pro v2.5 es el resultado de integrar "
            "eficiencia técnica con una experiencia de usuario intuitiva.\n\n"
            "Mi enfoque se centra en crear herramientas robustas que transforman datos complejos en "
            "decisiones estratégicas. Disponible para proyectos de software a medida, automatización "
            "de inventarios y consultoría tecnológica."
        )
        
        tk.Label(bio_card, text=bio_texto, font=("Segoe UI", 10), bg="white", 
                 justify="left", wraplength=900, fg="#444").pack(anchor="w")

        # --- SECCIÓN: CONTACTO Y REDES (2 Columnas) ---
        info_frame = tk.Frame(body_frame, bg="white")
        info_frame.pack(fill="both", expand=True)

        # Columna Izquierda: Contacto Directo
        left_col = tk.LabelFrame(info_frame, text=" Canales de Contacto ", font=("Segoe UI", 11, "bold"),
                                 bg="white", padx=20, pady=15, fg=COLOR_PRIMARY, relief="flat",
                                 highlightthickness=1, highlightbackground="#e0e0e0")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        contactos = [
            ("🔹", "Soporte Técnico:", "op2020pk@gmail.com"),
            ("🔹", "WhatsApp Business:", "+58 412-367-9938"),
            ("🔹", "Ubicación:", "Venezuela / Global")
        ]

        for icon, label, value in contactos:
            f = tk.Frame(left_col, bg="white")
            f.pack(anchor="w", pady=5)
            tk.Label(f, text=f"{icon} {label}", font=("Segoe UI", 9, "bold"), bg="white", width=18, anchor="w").pack(side="left")
            tk.Label(f, text=value, font=("Segoe UI", 9), bg="white", fg=COLOR_ACCENT).pack(side="left")

        # Columna Derecha: Redes y Portafolio
        right_col = tk.LabelFrame(info_frame, text=" Presencia Digital ", font=("Segoe UI", 11, "bold"),
                                  bg="white", padx=20, pady=15, fg=COLOR_PRIMARY, relief="flat",
                                  highlightthickness=1, highlightbackground="#e0e0e0")
        right_col.pack(side="left", fill="both", expand=True, padx=(10, 0))

        redes = [
            ("🔹", "GitHub:", "github.com/op2020pk-ux"),
            ("🔹", "Facebook:", "op2020pk@hotmail.com"),
        ]

        for icon, label, value in redes:
            f = tk.Frame(right_col, bg="white")
            f.pack(anchor="w", pady=5)
            tk.Label(f, text=f"{icon} {label}", font=("Segoe UI", 9, "bold"), bg="white", width=15, anchor="w").pack(side="left")
            tk.Label(f, text=value, font=("Segoe UI", 9), bg="white", fg=COLOR_SUCCESS).pack(side="left")

        # Pie de página de la pestaña
        footer_note = tk.Label(container, text="© 2025 Developer Portfolio - Comprometido con la Excelencia Digital", 
                               font=("Segoe UI", 8, "italic"), bg="white", fg="gray")
        footer_note.pack(side="bottom", pady=20)




# ******************** LOGIN APP ******************** #

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acceso al Sistema")
        self.root.geometry("400x550")
        self.root.iconbitmap("Iconos\hacker.ico") 
        self.root.configure(bg=COLOR_PRIMARY)
        self.init_db()
        self.create_widgets()

    def init_db(self):
        self.conn = sqlite3.connect("control_gastos.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE, password TEXT, imagen_fondo TEXT, ruta_pdf TEXT)')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS movimientos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, año INTEGER, mes INTEGER, categoria TEXT, monto REAL, tipo TEXT, usuario_id INTEGER)''')
        self.conn.commit()

    def create_widgets(self):
        f = tk.Frame(self.root, bg="white", padx=30, pady=30); f.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(f, text="ACCESO", font=("Segoe UI", 20, "bold"), bg="white", fg=COLOR_PRIMARY).pack(pady=10)
        tk.Label(f, text="Usuario:", bg="white").pack(anchor="w")
        self.ent_user = tk.Entry(f, font=("Segoe UI", 12), width=25); self.ent_user.pack(pady=5)
        tk.Label(f, text="Contraseña:", bg="white").pack(anchor="w")
        self.ent_pass = tk.Entry(f, font=("Segoe UI", 12), show="*", width=25); self.ent_pass.pack(pady=5)
        tk.Button(f, text="ENTRAR", bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 11, "bold"), width=20, command=self.login).pack(pady=10)
        tk.Button(f, text="REGISTRAR", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 9), width=20, command=self.registrar).pack(pady=5)
        tk.Button(f, text="RECUPERAR CLAVE", bg="#95a5a6", fg="white", font=("Segoe UI", 8), width=20, command=self.recuperar_clave).pack(pady=5)

    def login(self):
        u, p = self.ent_user.get(), self.ent_pass.get()
        self.cursor.execute("SELECT id, usuario FROM usuarios WHERE usuario = ? AND password = ?", (u, p))
        res = self.cursor.fetchone()
        if res:
            self.conn.close(); self.root.destroy(); main_r = tk.Tk(); FinanzasPro(main_r, res[0], res[1]); main_r.mainloop()
        else: messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def registrar(self):
        u, p = self.ent_user.get(), self.ent_pass.get()
        if not u or not p: messagebox.showwarning("Atención", "Complete todos los campos"); return
        try:
            self.cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (u, p))
            self.conn.commit(); messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        except sqlite3.IntegrityError: messagebox.showerror("Error", "El usuario ya existe")

    def recuperar_clave(self):
        def consultar_db():
            user = ent_recuperar.get()
            self.cursor.execute("SELECT password FROM usuarios WHERE usuario = ?", (user,))
            resultado = self.cursor.fetchone()
            if resultado: 
                messagebox.showinfo("Recuperación", f"La contraseña para '{user}' es: {resultado[0]}")
                ventana_rec.destroy()
            else: messagebox.showerror("Error", "El usuario no existe en el sistema")
        ventana_rec = tk.Toplevel(self.root)
        ventana_rec.title("Recuperar Contraseña"); ventana_rec.geometry("300x200"); ventana_rec.configure(bg="white"); ventana_rec.grab_set()
        tk.Label(ventana_rec, text="Ingrese su nombre de usuario:", bg="white", font=("Segoe UI", 9)).pack(pady=20)
        ent_recuperar = tk.Entry(ventana_rec, font=("Segoe UI", 10), width=25); ent_recuperar.pack(pady=5)
        tk.Button(ventana_rec, text="Consultar", bg=COLOR_ACCENT, fg="white", command=consultar_db).pack(pady=20)




# ********************* INICIO DE LA APLICACIÓN ******************** #

if __name__ == "__main__":
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()