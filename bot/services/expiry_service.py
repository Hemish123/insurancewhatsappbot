# from datetime import date, timedelta
# from bot.models import Customer

# def get_expiring_customers():
#     customers = Customer.objects.all()   # 🔥 TEMP FIX
#     print("TOTAL CUSTOMERS:", customers)
#     return customers



from datetime import date, timedelta
from bot.models import Customer

def get_expiring_customers():

    today = date.today()
    limit = today + timedelta(days=5)   # 🔥 5 days window

    # 🔥 DEBUG START
    print("TODAY:", today)
    print("LIMIT:", limit)

    print("\nALL CUSTOMERS:")
    for c in Customer.objects.all():
        print(c.name, c.expiry_date)
    # 🔥 DEBUG END

    customers = Customer.objects.filter(
        expiry_date__gte=today,     # not expired
        expiry_date__lte=limit,     # within 5 days
        reminder_sent=False         # not already sent
    )

    print("EXPIRING CUSTOMERS:", list(customers))

    return customers



# def get_expiring_customers():
#     from bot.models import Customer

#     customers = Customer.objects.all()   # 🔥 TEMP
#     print("TOTAL CUSTOMERS:", customers)

#     return customers