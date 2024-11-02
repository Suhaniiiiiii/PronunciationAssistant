def create_pronunciation_section(self):
    #     # Header Section
    #     header_frame = tk.Frame(self.root, bg='#00796b', height=80)
    #     header_frame.pack(fill=tk.X)

    #     self.label = tk.Label(header_frame, text=f"Welcome, {self.username}!", font=("Arial", 20, "bold"), bg='#00796b', fg='white')
    #     self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    #     # Logout Button
    #     self.logout_button = tk.Button(header_frame, text="Logout", command=self.logout, font=("Arial", 12, "bold"), bg="#ff5252", fg="white")
    #     self.logout_button.place(relx=0.93, rely=0.5, anchor=tk.CENTER)

    #     # Body Frame
    #     body_frame = tk.Frame(self.root, bg='#e0f7fa')
    #     body_frame.pack(pady=30)

    #     # Sentence Input Section
    #     input_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
    #     input_frame.pack(pady=10)

    #     sentence_label = tk.Label(input_frame, text="Enter or Get a Random Sentence:", font=("Arial", 14), bg='#b2dfdb')
    #     sentence_label.grid(row=0, column=0, columnspan=2, pady=10)

    #     self.custom_sentence_entry = tk.Entry(input_frame, font=("Arial", 14), width=50)
    #     self.custom_sentence_entry.grid(row=1, column=0, columnspan=2, pady=10)

    #     self.random_sentence_button = tk.Button(input_frame, text="Get Random Sentence", command=self.get_random_sentence, font=("Arial", 12), bg="#00796b", fg="white")
    #     self.random_sentence_button.grid(row=2, column=0, padx=10, pady=10)

    #     self.type_sentence_button = tk.Button(input_frame, text="Type Your Sentence", command=self.type_sentence, font=("Arial", 12), bg="#00796b", fg="white")
    #     self.type_sentence_button.grid(row=2, column=1, padx=10, pady=10)

    #     # Object Detection Button
    #     button_frame = tk.Frame(body_frame, bg='#e0f7fa')
    #     button_frame.pack(pady=20)

    #     self.record_button = tk.Button(button_frame, text="Record Pronunciation", command=self.record_sentence, font=("Arial", 14), bg="#00796b", fg="white")
    #     self.record_button.grid(row=0, column=0, padx=20)

    #     self.graph_button = tk.Button(button_frame, text="Show Score Graph", command=self.show_graph, font=("Arial", 14), bg="#00796b", fg="white")
    #     self.graph_button.grid(row=0, column=1, padx=20)

    #     # Pronunciation Recording Section
    #     record_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
    #     record_frame.pack(pady=10)

    #     self.progress = Progressbar(record_frame, length=200, mode='determinate')
    #     self.progress.grid(row=1, column=1, padx=10, pady=10)

    #     # Results Display Section
    #     result_frame = tk.Frame(body_frame, bg='#b2dfdb', padx=20, pady=20)
    #     result_frame.pack(pady=10)

    #     self.result_text = tk.Text(result_frame, height=6, width=65, bg='#ffffff', fg='black', font=("Arial", 12), relief=tk.SUNKEN)
    #     self.result_text.pack(pady=10)