import importlib


def reset_modules():
    # Reload modules to start from a known state
    import Parcel_Registration
    import Parcel_Management
    import Parcel_LiveTracking
    import Parcel_Reports
    import app

    Parcel_Registration.parcel_database.clear()
    Parcel_Management.parcel_database.clear()
    Parcel_Management.delivery_queue.clear()
    Parcel_LiveTracking.parcel_database.clear()
    Parcel_Reports.parcel_database = Parcel_Management.parcel_database

    return Parcel_Registration, Parcel_Management, Parcel_LiveTracking, Parcel_Reports, app


def test_parcel_progresses_through_stages_and_tracks_history():
    reg, mgmt, tracking, reports, flask_app = reset_modules()

    parcel = reg.register_parcel('Alice', 'Bob')
    assert parcel is not None

    mgmt.add_to_queue(parcel.tracking_id)

    assert parcel.status == 'Registered'
    assert parcel in mgmt.parcel_database
    assert parcel in mgmt.delivery_queue

    mgmt.process_next()
    assert parcel.status == 'Picked Up'
    assert len(parcel.history) == 2

    mgmt.process_next()
    assert parcel.status == 'In Transit'

    mgmt.process_next()
    assert parcel.status == 'Out for Delivery'

    mgmt.process_next()
    assert parcel.status == 'Delivered'
    assert parcel not in mgmt.delivery_queue

    tracked = tracking.binary_search(parcel.tracking_id)
    assert tracked is not None
    assert tracked.status == 'Delivered'
    assert len(tracked.history) == 5

    stats = reports.ReportGenerator.get_statistics()
    assert stats['delivered'] == 1
    assert stats['total'] == 1
