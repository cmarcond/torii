import json
from devias.app import project_info, report_info 
from datetime import datetime
from dateutil.relativedelta import relativedelta


def format_date_time(date):
    """Formats date as YYYY-MM-DD."""

    formatted_date = date[6:10] + "-" + date[3:5] + "-" + date[0:2]
    return formatted_date


def get_all_project_dates(gl):
    """Lists all dates with project submissions, including 
    number of projects submitted each day.
    
    Args:
        gl (gitlab.Gitlab object): Gitlab session object.
    
    Returns:
        str: json dumped dict with each key:value pair associated with every 
        project submission date and number of projects submitted that day.
    """
    
    dates = {}

    items = gl.projects.list(owned=True, all=True, as_list=False)

    for item in items._list._data:
        project = project_info.get(item["id"])

        if project is not None:
            project = json.loads(project)
            uuid_list = project["uuid"]

            # print(f"UUID list: {uuid_list}")

            if type(uuid_list) is dict:
                current_version = len(uuid_list)
                report = report_info.get(uuid_list[f"{current_version}"])

            elif type(uuid_list) is str:
                report = report_info.get(uuid_list)


                # for uuid_key in uuid_list:
                #     report = report_info.get(uuid_list[uuid_key])

            if report is not None:
                report = json.loads(report)
                date = report["date"]

                # new date time format dd/mm/yyyy time UTC
                if len(date) > 10:
                    date = format_date_time(date)

                if date in dates and "number_findings" in report:
                    dates[date] = dates[date] + int(report["number_findings"])
                elif "number_findings" in report:
                    dates[date] = int(report["number_findings"])

    formatted_dates = json.dumps(dates)

    return formatted_dates


def get_recent_projects(gl):
    """Lists IDs of all projects submitted in the last 30 days.

    Args:
        gl (gitlab.Gitlab object): Gitlab session object.
    
    Returns:
        list: List of recent project IDs.
    """

    current_date = datetime.now()
    past_date = current_date - relativedelta(months=1)
    past_date = past_date.isoformat()

    items = gl.projects.list(owned=True, all=True, last_activity_after=past_date)
    
    id_list = []
    
    for item in items:
        id_list.append(item.get_id())

    return id_list


def get_uuid_list(id_list):
    """Lists the UUIDs of the most recent version of each 
    project submitted in the last 30 days.
    
    Args: 
        id_list (list): list of recent project IDs.

    Returns:
        list: list of recent project UUIDs.\
    """

    uuid_list = []

    for id in id_list:
        project = project_info.get(f"{id}")

        if project is not None:
            project = json.loads(project)

            uuid_dict = project["uuid"]

            if type(uuid_dict) is dict:
                current_version = len(uuid_dict)
                uuid_list.append(uuid_dict[f"{current_version}"])

            elif type(uuid_dict) is str:
                uuid_list.append(uuid_dict)

    return uuid_list


def get_report_info(uuid_list):
    """Lists reports for each project (latest version) submitted in the last 30 days.

    Args:
        uuid_list (list): list of recent project UUIDs.

    Returns:
        list: list of recent project reports.
    """

    report_list = []

    for uuid in uuid_list:
        report = report_info.get(f"{uuid}")

        if report is not None:
            report = json.loads(report)
            report_list.append(report)

    return report_list
        

def get_recent_stats(gl):
    """Compiles the number of findings according to severity and vulnerability types
    from projects submitted in the last 30 days.

    Args:
        gl (gitlab.Gitlab object): Gitlab session object

    Returns:
        dict: dict containing the total number of findings, 
        severity types and vulnerability types. 
    """

    recent_project_ids = get_recent_projects(gl)
    project_uuid_list = get_uuid_list(recent_project_ids)
    report_list = get_report_info(project_uuid_list)

    total_number_findings = 0
    total_critical_findings = 0
    total_high_findings = 0
    total_medium_findings = 0
    total_low_findings = 0 
    total_info_findings = 0
    
    total_SAST_findings = 0
    total_containers_findings = 0
    total_secrets_findings = 0
    total_component_findings = 0

    for report in report_list:
        if "number_findings" in report:
            total_number_findings += int(report["number_findings"])

            total_critical_findings += int(report["severity_types"]["critical"])
            total_high_findings += int(report["severity_types"]["high"])
            total_medium_findings += int(report["severity_types"]["medium"])
            total_low_findings += int(report["severity_types"]["low"])
            total_info_findings += int(report["severity_types"]["info"])

            total_SAST_findings += int(report["vuln_types"]["SAST"])
            total_containers_findings += int(report["vuln_types"]["containers"])
            total_secrets_findings += int(report["vuln_types"]["secrets"])
            total_component_findings += int(report["vuln_types"]["component"])

    recent_stats = {
        "total_findings": total_number_findings,
        "severity": {
            "critical": total_critical_findings,
            "high": total_high_findings,
            "medium": total_medium_findings,
            "low": total_low_findings,
            "info": total_info_findings,
        },
        "types": {
            "SAST": total_SAST_findings,
            "containers": total_containers_findings,
            "secrets": total_secrets_findings,
            "SCA": total_component_findings,
        },
    }

    return recent_stats

