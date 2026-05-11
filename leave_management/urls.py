from django.urls import path

from leave_management.views import (approve_leave_request, create_leave_request, create_leave_type, delete_leave_type,
                                    get_leave_balances, get_leave_requests, cancel_leave_request, get_leave_types,
                                    get_pending_leave_requests, get_rejected_leave_requests, get_rejected_leave_requests,
                                    reject_leave_request, update_leave_balance, update_leave_type, get_all_leave_requests, get_approved_leave_requests,
                                    get_all_leave_balances)

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
    path("get_leave_types/", get_leave_types, name="get_leave_types"),
    path("create_leave_type/", create_leave_type, name="create_leave_type"),
    path("update_leave_type/", update_leave_type, name="update_leave_type"),
    path("delete_leave_type/", delete_leave_type, name="delete_leave_type"),
    path("get_all_leave_requests/", get_all_leave_requests,name="get_all_leave_requests"),
    path("get_all_leave_balances/", get_all_leave_balances, name="get_all_leave_balances"),
    path("update_leave_balance/", update_leave_balance, name="update_leave_balance"),
]