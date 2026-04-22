from django.urls import path

from leave_management.views import (approve_leave_request, create_leave_request, get_approved_leave_requests,
                                    get_leave_balances, get_leave_requests, cancel_leave_request,
                                    get_pending_leave_requests, get_rejected_leave_requests, get_rejected_leave_requests,
                                    reject_leave_request)

urlpatterns = [
    # Add URL patterns for leave management here
    path("create_leave_request/", create_leave_request, name="create_leave_request"),
    path("get_leave_requests/", get_leave_requests, name="get_leave_requests"),
    path("get_leave_balances/", get_leave_balances, name="get_leave_balances"),
    path("cancel_leave_request/", cancel_leave_request, name="cancel_leave_request"),
    path("get_pending_leave_requests/", get_pending_leave_requests, name="get_pending_leave_requests"),
    path("approve_leave_request/", approve_leave_request, name="approve_leave_request"),
    path("reject_leave_request/", reject_leave_request, name="reject_leave_request"),
    path("get_approved_leave_requests/", get_approved_leave_requests, name="get_approved_leave_requests"),
    path("get_rejected_leave_requests/", get_rejected_leave_requests, name="get_rejected_leave_requests"),
]