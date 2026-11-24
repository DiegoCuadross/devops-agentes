from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

# Modelos en orden de preferencia: si uno falla (por ejemplo, 503 por
# saturación), se prueba el siguiente.
MODELOS = [
    "gemini/gemini-3.5-flash-lite",
    "gemini/gemini-3.1-flash-lite",
    "gemini/gemini-2.5-flash",
    "gemini/gemini-3.8-flash",
]

perfil = Path("perfil.txt").read_text(encoding="utf-8")
oferta = Path("oferta.txt").read_text(encoding="utf-8")


def crear_equipo(llm):
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
Usa solo lo que dice el perfil y no inventes habilidades ni experiencia.
Entrega: coincidencia aproximada, fortalezas, vacíos y 3 pasos concretos para cerrarlos.

PERFIL:
{perfil}""",
        expected_output="Informe en español, en Markdown, de máximo 250 palabras.",
        agent=evaluador,
        context=[tarea_extraer],
        output_file="informe.md",
    )

    return Crew(
        agents=[extractor, evaluador],
        tasks=[tarea_extraer, tarea_evaluar],
        process=Process.sequential,
    )


for modelo in MODELOS:
    print(f"\n>>> Probando con el modelo {modelo}...\n")
    try:
        resultado = crear_equipo(LLM(model=modelo)).kickoff()
        break
    except Exception as error:
        print(f"\n>>> El modelo {modelo} falló: {error}\n")
else:
    raise SystemExit("Todos los modelos fallaron. Espera unos minutos e intenta de nuevo.")

print(f"\n>>> Análisis hecho con {modelo}\n")
print(resultado)
