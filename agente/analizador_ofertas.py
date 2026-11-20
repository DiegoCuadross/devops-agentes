from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

llm = LLM(model="gemini/gemini-3.5-flash-lite")

perfil = Path("perfil.txt").read_text(encoding="utf-8")
oferta = Path("oferta.txt").read_text(encoding="utf-8")

extractor = Agent(
    role="Analista de ofertas de empleo",
    goal="Extraer con precisión los requisitos de una oferta de trabajo",
    backstory="Eres un reclutador técnico que separa lo obligatorio de lo deseable.",
    llm=llm,
)

evaluador = Agent(
    role="Mentor de carrera en ingeniería de sistemas",
    goal="Comparar el perfil de un candidato con una oferta y decir qué le falta aprender",
    backstory="Eres un ingeniero senior, honesto y práctico, que ayuda a conseguir el primer empleo.",
    llm=llm,
)

tarea_extraer = Task(
    description=f"""Lee esta oferta y extrae: cargo, requisitos obligatorios,
requisitos deseables, tecnologías y experiencia pedida.

OFERTA:
{oferta}""",
    expected_output="Lista en español con: Cargo, Obligatorios, Deseables, Tecnologías, Experiencia.",
    agent=extractor,
)

tarea_evaluar = Task(
    description=f"""Compara los requisitos extraídos con este perfil.
Usa solo lo que dice el perfil y no inventes habilidades.
Entrega: coincidencia aproximada, fortalezas, vacíos y 3 pasos concretos para cerrarlos.

PERFIL:
{perfil}""",
    expected_output="Informe en español, en Markdown, de máximo 250 palabras.",
    agent=evaluador,
    context=[tarea_extraer],
    output_file="informe.md",
)

equipo = Crew(
    agents=[extractor, evaluador],
    tasks=[tarea_extraer, tarea_evaluar],
    process=Process.sequential,
)

resultado = equipo.kickoff()
print(resultado)