import tkinter as tk
from math import tan, radians, asin, sin, cos, degrees

class Geometry:
    def __init__(self, width, height) -> None:
        self.w = width
        self.h = height

def on_close():
    global runing
    master.destroy()
    runing = False

def map_range(value, start1, stop1, start2, stop2):
   return (value - start1) / (stop1 - start1) * (stop2 - start2) + start2

def add_mat():
    if len(materials) < 5:
        materials.append([
            tk.StringVar(),
            tk.StringVar(),
            ])
        materials[len(materials)-1].append([
                tk.Label(mat_frame, text="Material", font=('calibre',10, 'bold')),
                tk.Entry(mat_frame, textvariable=materials[len(materials)-1][0], font=('calibre',10, 'bold'), width=10),
                tk.Label(mat_frame, text="Índex", font=('calibre',10, 'bold')),
                tk.Entry(mat_frame, textvariable=materials[len(materials)-1][1], font=('calibre',10, 'bold'), width=10)
                ])
        for i in range(4):
            materials[len(materials)-1][2][i].grid(row=len(materials), column=i)

def rem_mat():
    for item in range(4):
        materials[len(materials)-1][2][item].destroy()
    materials.pop(len(materials)-1)

materials = [] # LLISTA DELS ÍNDEX DELS MATERIALS

master = tk.Tk()
master.geometry("1000x700")
mat_frame = tk.Frame(master)
mat_frame.pack(padx=10, pady=10)
button_frame = tk.Frame(master)
button_frame.pack()
results_frame=tk.Frame(master)
results_frame.pack()
angle_frame = tk.Frame(master)
angle_frame.pack()

master.protocol("WM_DELETE_WINDOW", on_close)
master.winfo_toplevel().title("Coeficients i Factors de Fresnel - Marc Parcerisa i Conesa")
tk.Button(button_frame, text="Afegir Material", command=add_mat, font=('calibre',10, 'bold')).grid(column=0, row=0, padx=10)
tk.Button(button_frame, text="Eliminar Material", command=rem_mat, font=('calibre',10, 'bold')).grid(column=1, row=0, padx=10)

angle = tk.StringVar()
tk.Label(angle_frame, text = "Angle d'incidència (º)", font = ('calibre',10, 'bold')).grid(column=0, row=0)
tk.Entry(angle_frame, textvariable=angle, font=('calibre',10, 'bold')).grid(column=1, row=0)


geometry = Geometry(400, 400)

canvas = tk.Canvas(results_frame, width=geometry.w, height=geometry.h, bg="white")
canvas.grid(column=0, row=0,pady=20)
text_frame = tk.Frame(results_frame)
text_frame.grid(column=1, row=0, pady=20, padx=20)
text_resultats = tk.StringVar()
tk.Label(text_frame, textvariable=text_resultats, font=('calibre', 10, 'bold')).grid(row=0)

def get_color(n):
    if n.get() != "":
        index = float(n.get())
    else:
        index = 1
    if n_range[0] == n_range[1]:
        return("#ffffff")
    return("#"+hex(int(map_range(index, n_range[0], n_range[1], 255, 128))).replace("0x", "")*3)

def draw_materials():
    if len(materials) != 0:
        for i in range(len(materials)):
            canvas.create_rectangle(2, i*H+2, geometry.w+2, (i+1)*H+2, fill=get_color(materials[i][1]), width=2)
            canvas.create_text(geometry.w-70, H*(i+1/2), text=f"{materials[i][0].get()} (n={materials[i][1].get()})", font=('calibre',10, 'bold'))
    else:
        canvas.delete("all")
        
def get_n_range():
    Ns = []
    for mat in materials:
        if mat[1].get() != '':
            Ns.append(float(mat[1].get()))
        else:
            Ns.append(1)
    try:
        return [min(Ns), max(Ns)]
    except:
        return [1, 1]

def calculate_transmitted_rays():
    if len(materials) != 0:
        rays = [[0, 0, radians(float(angle.get()))]]
        for i in range(len(materials)-1):
            x0 = rays[i][0]
            y0 = rays[i][1]
            theta0 = rays[i][2]
            try:
                new_theta = asin(float(materials[i][1].get())/float(materials[i+1][1].get()) * sin(theta0))
            except:
                # rays.append([0,0,0])
                return rays
            rays.append([x0 + H*tan(theta0), y0 + H,new_theta])
        rays = translate_rays(rays)
    else:
        rays = []
    return rays

def translate_rays(rays):
    X = []
    if len(rays) != 1:
        for ray in range(len(rays)-1):
            X.append(rays[ray+1][0])
    else:
        X = [rays[0][0], rays[0][0]+H*tan(rays[0][2])]
    distance = (max(X)+min(X))/2 - geometry.w/2
    return [[ray[0]-distance, ray[1], ray[2]] for ray in rays]

def draw_rays():
    global rays
    rays = calculate_transmitted_rays()
    for pt in rays:
        canvas.create_line(pt[0], pt[1], pt[0]+H*tan(pt[2]), pt[1]+H, fill="lime", width=2)
        text_x = pt[0]+30 + H*tan(pt[2])/2
        if text_x < 30:
            text_x = 30
        elif text_x > geometry.w-30:
            text_x = geometry.w-30
        canvas.create_text(text_x, pt[1] + H/2, text="%.2fº" % degrees(pt[2]), font=('calibre', 10, 'bold'), fill='lime')
    for i in range(len(rays)):
        pt = rays[i]
        if i != len(materials)-1:
            if materials[i][1].get() != materials[i+1][1].get():
                canvas.create_line(pt[0]+H*tan(pt[2]), pt[1]+H, pt[0]+2*H*tan(pt[2]), pt[1], fill="lime", width=2)

def purge_values():
    for i in range(len(materials)):
        try:
            float(materials[i][1].get())
        except:
            materials[i][1].set("1")
    try:
        float(angle.get())
        assert float(angle.get()) < 90 and float(angle.get()) > 0
    except:
        angle.set("0")

def update_results():
    text_base = "Coeficients i Factors\nInterfase\tt (||)\tt (┴)\tr (||)\tr (┴)\tT (||)\tT (┴)\tR (||)\tR(┴)"
    for r in range(len(rays)):
        if r == len(rays)-1 and len(rays) != len(materials):
            text_base+="\nHi ha reflexió total"
        elif r != len(rays)-1:
            th0 = rays[r][2]
            th1 = rays[r+1][2]
            n0 = float(materials[r][1].get())
            n1 = float(materials[r+1][1].get())
            if th0 != th1:
                t_II = (2*sin(th1)*cos(th0))/(sin(th1+th0)*cos(th1-th0))
                t_T = (2*sin(th1)*cos(th0))/(sin(th1+th0))
                r_II = tan(th1-th0)/tan(th1+th0)
                r_T = sin(th1-th0)/sin(th1+th0)
            else: #Incidència normal
                t_II = 2*n0/(n0+n1)
                t_T = t_II
                r_II = (n0-n1)/(n0+n1)
                r_T = r_II
            T_II = t_II**2 * (n1*cos(th1))/(n0*cos(th0))
            T_T = t_T**2 * (n1*cos(th1))/(n0*cos(th0))
            R_II = 1-T_II
            R_T = 1-T_T

            text_base += "\n%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f" % (r,t_II,t_T,r_II,r_T,T_II,T_T,R_II,R_T)
    text_resultats.set(text_base)

runing = True
while runing:
    if len(materials) != 0:
        H = geometry.h/len(materials)
    else:
        H=geometry.h
    try:
        canvas.delete("all")
    except:
        pass
    purge_values()
    n_range = get_n_range()
    draw_materials()
    draw_rays()
    update_results()
    master.update_idletasks()
    master.update()
