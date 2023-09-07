from datetime import date

def format_report_vuln(data):
    """Separates report vulnerabilities by type.

    Args:
        data (json): Report json.

    Returns:
        SAST_report (list): list containing SAST type vulnerabilities.
        Containers_report (list): list containing container type vulnerabilitites.
        Secrets_report (list): list containing secrets.
        SCA_report (list): list containing SCA analysis vulnerabilities.
    """
    
    SAST_report = []
    Containers_report = []
    Secrets_report = []
    SCA_report = []


    for item in range(data['number_findings']):
        if data[str(item)]['type'] == 'SAST':
            SAST_report.append(data[str(item)])
        elif data[str(item)]['type'] == 'CONTAINERS':
            Containers_report.append(data[str(item)])
        elif data[str(item)]['type'] == 'SECRETS':
            Secrets_report.append(data[str(item)])
        elif data[str(item)]['type'] == 'SCA':
            SCA_report.append(data[str(item)])

    return SAST_report, Containers_report, Secrets_report, SCA_report


def format_report_sev(data):
    """Separates vulnerabilities by severity

    Args:
        data (json): Report json.

    Returns:
        Critical (list): List of critical vulnerabilities.
        High (list): List of high severity vulnerabilities.
        Medium (list): List of medium severity vulnerabilities.
        Low (list): List of low severity vulnerabilities.
        Info (list): List of informative vulnerabilities.
    """

    Critical = []
    High = []
    Medium = []
    Low = []
    Info = []


    for item in range(data['number_findings']):
        if data[str(item)]['severity'] == 'Crítica':
            Critical.append(data[str(item)])
        elif data[str(item)]['severity'] == 'Alta':
            High.append(data[str(item)])
        elif data[str(item)]['severity'] == 'Média':
            Medium.append(data[str(item)])
        elif data[str(item)]['severity'] == 'Baixa':
            Low.append(data[str(item)])
        elif data[str(item)]['severity'] == 'Informativa':
            Info.append(data[str(item)])


    return Critical, High, Medium, Low, Info


def get_report_datetime(data):
    """Formats project submission date

    Args: 
        data (json): Report json.
    
    Returns:
        str: converted date and time.
    """

    submission_info = data['report_info']
    date_time = submission_info[-22:]

    # invert month and day
    converted_date_time = date_time[3:6] + date_time[0:3] + date_time[6:]
    print(converted_date_time)

    return converted_date_time



def write_report_info(data, Critical, High, Medium, Low, Info, SAST_report, Containers_report, Secrets_report, SCA_report):
    """Compiles report statistics

    Args:
        data (json): Report json.
        Critical, High, Medium, Low, Info (list): Lists of 
        vulnerabilities separated by severity. 
        SAST_report, Containers_report, Secrets_report, SCA_report (list):
        Lists of vulnerabilities separated by type.

    Returns:
        dict: dict containing project info (date, findings, vulnerabilities 
        by severity and by type).
    """
    
    date_time = get_report_datetime(data)
    
    project = {
        "date": date_time,
        "number_findings": f"{data['number_findings']}",
        "severity_types": {
            "critical": f"{len(Critical)}",
            "high": f"{len(High)}",
            "medium": f"{len(Medium)}",
            "low": f"{len(Low)}",
            "info": f"{len(Info)}",
        },
        "vuln_types": {
            "SAST": f"{len(SAST_report)}",
            "containers": f"{len(Containers_report)}",
            "secrets": f"{len(Secrets_report)}",
            "component": f"{len(SCA_report)}",
        },
    }

    return project