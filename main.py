#Importamos los modulos o dependencias del programa
import random
import math
from array import array

#arcade dependencia principal
import arcade.gui
import arcade
from arcade.gl import BufferDescription

#para la ventana de bienvenida
import tkinter as tk
from tkinter import simpledialog, messagebox

# Dimensiones de la ventana del simulador
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# Gráfica de rendimiento
GRAPH_WIDTH = 260
GRAPH_HEIGHT = 180
GRAPH_MARGIN = 5

#campo de vision
STARFIELD_RADIUS = 200

# Mensajes de Windows personalizado
root = tk.Tk()
root.withdraw()
messagebox.showinfo("Simulador de N Cuerpos", "¡Hola, Usuario!")

# Dimensiones y título de la ventana del menú interactivo
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Simulador de N Cuerpos"


class MainView(arcade.View):
    """Vista principal del sim."""

    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        switch_menu_button = arcade.gui.UIFlatButton(text="Iniciar", width=250)

        # Inicializa el botón con un evento on_click
        @switch_menu_button.event("on_click")
        def on_click_switch_button(event):
            self.window.show_view(SimulatorView(self.window))

        # Usa el anclaje para posicionar el botón en la pantalla
        #posicion del boton
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=switch_menu_button,
        )

    def on_hide_view(self):
        # Deshabilita el UIManager cuando la vista se oculta
        self.manager.disable()

    def on_show_view(self):
        """Se ejecuta una vez cuando cambiamos a esta vista."""
        arcade.set_background_color(arcade.color.BLACK)
        self.manager.enable()

    def on_draw(self):
        """Renderiza la pantalla."""
        self.clear()
        self.manager.draw()


#sim
class SimulatorView(arcade.View):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

        self.num_stars = 23000
        self.group_x = 256
        self.group_y = 1

        buffer_format = "4f 4x4 4f"
        initial_data = self.gen_random_space()
                      #gen_galaxies_colliding
                      #gen_random_space

        self.ssbo_1 = self.window.ctx.buffer(data=array('f', initial_data))
        self.ssbo_2 = self.window.ctx.buffer(reserve=self.ssbo_1.size)

        attributes = ["in_vertex", "in_color"]
        self.vao_1 = self.window.ctx.geometry([BufferDescription(self.ssbo_1, buffer_format, attributes)], mode=self.window.ctx.POINTS)
        self.vao_2 = self.window.ctx.geometry([BufferDescription(self.ssbo_2, buffer_format, attributes)], mode=self.window.ctx.POINTS)

        #busca archivos de los que depende el programa
        with open("shaders/compute_shader.glsl") as file:
            compute_shader_source = file.read()
        with open("shaders/vertex_shader.glsl") as file:
            vertex_shader_source = file.read()
        with open("shaders/fragment_shader.glsl") as file:
            fragment_shader_source = file.read()
        with open("shaders/geometry_shader.glsl") as file:
            geometry_shader_source = file.read()

        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_X", str(self.group_x))
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_Y", str(self.group_y))
        self.compute_shader = self.window.ctx.compute_shader(source=compute_shader_source)

        self.program = self.window.ctx.program(vertex_shader=vertex_shader_source, geometry_shader=geometry_shader_source, fragment_shader=fragment_shader_source)

        #llama la grafica de rendimiento
        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS", )
        graph.center_x = GRAPH_WIDTH / 2
        graph.center_y = self.window.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

    def on_draw(self):
        self.clear()
        self.window.ctx.enable(self.window.ctx.BLEND)
        self.ssbo_1.bind_to_storage_buffer(binding=0)
        self.ssbo_2.bind_to_storage_buffer(binding=1)
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)
        self.vao_2.render(self.program)
        self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1
        self.perf_graph_list.draw()

    #funcion del menu en pausa de sim (error la simulacion sigue corriendo)!!
    def on_key_press(self, key, modifiers):
        """Cambia al menú principal al presionar ESC."""
        if key == arcade.key.ESCAPE:
            self.window.show_view(MainView())

    #funcion de la primera sim
    def gen_random_space(self):
        radius = 3.0
        for i in range(self.num_stars):
            yield random.random() * WINDOW_WIDTH
            yield random.random() * WINDOW_HEIGHT
            yield random.random() * WINDOW_HEIGHT
            yield radius
            yield 0.0
            yield 0.0
            yield 0.0
            yield 0.0
            yield 1.0
            yield 1.0
            yield 1.0
            yield 1.0

    #funcion de la segunda sim
    def gen_galaxies_colliding(self):
        radius = 3.0
        for i in range(self.num_stars):
            angle = random.random() * math.pi * 2
            angle2 = random.random() * math.pi * 2
            distance = random.random() * STARFIELD_RADIUS

            if i % 2 == 0:
                yield distance * math.cos(angle) - STARFIELD_RADIUS
            else:
                yield distance * math.cos(angle) + STARFIELD_RADIUS + WINDOW_WIDTH
            yield distance * math.sin(angle) + WINDOW_HEIGHT / 2
            yield distance * math.sin(angle2)
            yield radius
            yield math.cos(angle + math.pi / 2) * distance / 100
            yield math.sin(angle + math.pi / 2) * distance / 100
            yield math.sin(angle2 + math.pi / 2) * distance / 100
            yield 0.0
            yield 1.0
            yield 1.0
            yield 1.0
            yield 1.0

#funcion que permite corre el menu de inicio
def run_menu():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    main_view = MainView()
    window.show_view(main_view)
    arcade.run()

#se crea la funcion main, adentro se hace referencia a la funcion del menu
def main():
    run_menu()

#permite que main sea llamado cuando se ejecuta el codigo anterior
if __name__ == "__main__":
    main()
