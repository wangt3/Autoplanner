def example1():
    def print_sel():
        print(cal.selection_get())

    top = tk.Toplevel(root)

    cal = Calendar(top, font="Arial 14", selectmode='day', locale='en_US',
                year=2018, month=2, day=5)
    
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="ok", command=print_sel).pack()

    
def example2():

    top = tk.Toplevel(root)
    top.update_idletasks()
    cal = Calendar(top, selectmode='none')
    date = cal.datetime.today() + cal.timedelta(days=2)
    cal.calevent_create(date, 'Hello World', 'message')
    cal.calevent_create(date, 'Reminder 2', 'reminder')
    cal.calevent_create(date + cal.timedelta(days=-2), 'Reminder 1', 'reminder')
    cal.calevent_create(date + cal.timedelta(days=3), 'Message', 'message')

    cal.tag_config('reminder', background='red', foreground='yellow')

    cal.pack(fill="both", expand=True)
    ttk.Label(top, text="Hover over the events.").pack()
    top.update_idletasks()