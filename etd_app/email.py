from __future__ import unicode_literals
from django.core.mail import send_mail
from django.utils import timezone


FROM_ADDRESS = 'etd@brown.edu'

ACCEPT_MSG_TEMPLATE = '''Dear {first_name} {last_name},

The manuscript of your dissertation, "{title}", satisfies all of the Graduate School's formatting requirements.

If you have not already done so, please submit all required paperwork to fulfill your completion requirements. As this paperwork is received, you will be notified (via the email address stored in your profile on the ETD system) and the Graduate School will update the checklist that appears on to the ETD website (http://library.brown.edu/etd).

Sincerely,
The Brown University Graduate School'''

REJECT_MSG_TEMPLATE = '''"Dear {first_name} {last_name},

Your dissertation, "{title}", needs revision before it can be accepted by the Graduate School. The details of these required revisions are below:

{issues}

Please resubmit your dissertation once you have addressed the issues above. If you have any questions about these issues, please contact the Graduate School at Graduate_School@brown.edu or 401-863-2843.

Sincerely,
The Brown University Graduate School'''

PAPERWORK_INFO = {
        'dissertation_fee': {'subject': 'Dissertation Fee', 'email_snippet': 'Cashier\'s Office receipt was'},
        'bursar_receipt': {'subject': 'Bursar\'s Letter', 'email_snippet': 'Bursar\'s Office letter of clearance was'},
        'gradschool_exit_survey': {'subject': 'Graduate Exit Survey', 'email_snippet': 'graduate exit survey was'},
        'earned_docs_survey': {'subject': 'Survey of Earned Doctorates', 'email_snippet': 'Survey of Earned Doctorates was'},
        'pages_submitted_to_gradschool': {'subject': 'Signature Pages', 'email_snippet': 'signature, abstract, and title pages were'},
    }

PAPERWORK_MSG_TEMPLATE = '''Dear {first_name} {last_name},

Your {email_snippet} received by the Graduate School on {now}.

Please submit any outstanding paperwork that is required to fulfill your completion requirements. As this paperwork is received, you will be notified (via the email address stored in your profile on the ETD system) and the Graduate School will update the checklist that appears on to the ETD website (http://library.brown.edu/etd).

Sincerely,
The Brown University Graduate School'''

COMPLETE_MSG_TEMPLATE = '''Dear {first_name} {last_name},

Congratulations! Your dissertation, {title}, and all of the paperwork associated with your completion requirements have been received by the Graduate School. An official, written notification regarding the completion of your doctoral degree at Brown will be sent to you in the coming days (this email is automatically generated and, as such, is not an official communication).

For information about this year's Commencement exercises, please visit the University's Commencement website: http://www.brown.edu/commencement (the timeliness of the material on this site will depend on the date of your submission). If you have questions or concerns about your completion or the Commencement ceremony that are not addressed on the website, please send us email, Graduate_School@brown.edu.

Congratulations again on your accomplishment. All of Brown wishes you the best of luck and great success in your future.

Sincerely,
The Brown University Graduate School'''


def _get_formatting_issues_msg(candidate):
    format_checklist = candidate.thesis.format_checklist
    issues_msg = ''
    if format_checklist.general_comments:
        issues_msg += 'General Comments:\n%s\n\n' % format_checklist.general_comments
    issues_msg += 'These elements of your dissertation are not properly formatted:\n\n'
    if format_checklist.title_page_comment:
        issues_msg += 'Title page: %s\n\n' % format_checklist.title_page_comment
    if format_checklist.signature_page_comment:
        issues_msg += 'Signature page: %s\n\n' % format_checklist.signature_page_comment
    if format_checklist.font_comment:
        issues_msg += 'Font: %s\n\n' % format_checklist.font_comment
    if format_checklist.spacing_comment:
        issues_msg += 'Spacing: %s\n\n' % format_checklist.spacing_comment
    if format_checklist.margins_comment:
        issues_msg += 'Margins: %s\n\n' % format_checklist.margins_comment
    if format_checklist.pagination_comment:
        issues_msg += 'Pagination: %s\n\n' % format_checklist.pagination_comment
    if format_checklist.format_comment:
        issues_msg += 'Format: %s\n\n' % format_checklist.format_comment
    if format_checklist.graphs_comment:
        issues_msg += 'Graphs: %s\n\n' % format_checklist.graphs_comment
    if format_checklist.dating_comment:
        issues_msg += 'Dating: %s\n\n' % format_checklist.dating_comment
    return issues_msg


def _accept_params(candidate):
    params = {}
    params['subject'] = 'Dissertation Submission Approved'
    params['message'] = ACCEPT_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title)
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _reject_params(candidate):
    params = {}
    params['subject'] = 'Dissertation Submission Rejected'
    params['message'] = REJECT_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title,
                            issues=_get_formatting_issues_msg(candidate))
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _format_datetime_display(dt):
    return dt.strftime('%m/%d/%Y at %H:%M')


def _paperwork_params(candidate, item_completed):
    params = {}
    params['subject'] = PAPERWORK_INFO[item_completed]['subject']
    params['message'] = PAPERWORK_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            email_snippet=PAPERWORK_INFO[item_completed]['email_snippet'],
                            now=_format_datetime_display(timezone.now()))
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _complete_params(candidate):
    params = {}
    params['subject'] = 'Submission Process Complete'
    params['message'] = COMPLETE_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title)
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _send_email(params):
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)


def send_accept_email(candidate):
    params = _accept_params(candidate)
    _send_email(params)


def send_reject_email(candidate):
    params = _reject_params(candidate)
    _send_email(params)


def send_paperwork_email(candidate, item_completed):
    params = _paperwork_params(candidate, item_completed)
    _send_email(params)


def send_complete_email(candidate):
    params = _complete_params(candidate)
    _send_email(params)
