from orm.database import Session
from orm.models.execution_logs import ExecutionLogs


def insert_execution_logs(file_id: int, exit_code: int, execution_output: str):
    print("Instering execution logs")
    # perfrom insert
    with Session() as session:
        new_log = ExecutionLogs(
            file_id=file_id, exit_code=exit_code, execution_output=execution_output
        )
        session.add(new_log)
        session.commit()
