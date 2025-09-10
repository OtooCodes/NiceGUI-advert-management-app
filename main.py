from nicegui import ui
from pymongo import MongoClient
from bson.objectid import ObjectId

# ------------------- MongoDB Connection -------------------
# Replace <username>, <password>, and <cluster-url> with your actual details
MONGO_URI = "mongodb+srv://<username>:<password>@<cluster-url>/myDatabase?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

db = client["ad_management"]          # Database name
collection = db["adverts"]            # Collection name

# ------------------- Functions -------------------

def refresh_adverts():
    advert_container.clear()
    with advert_container:
        with ui.grid(columns=3).classes('gap-4 p-4'):
            for advert in collection.find():
                advert_id = str(advert["_id"])
                with ui.card().classes('p-4 shadow-lg hover:scale-105 transition-transform duration-300'):
                    ui.label(advert['title']).classes('text-xl font-bold text-gray-800')
                    ui.label(advert['description']).classes('text-gray-600')
                    ui.label(f"Price: ${advert['price']}").classes('text-green-600 font-semibold')
                    ui.label(f"Category: {advert['category']}").classes('text-sm text-gray-500')
                    with ui.row():
                        ui.button('Edit', on_click=lambda e, _id=advert_id: edit_advert(_id)).classes('bg-blue-500 text-white px-3 py-1 rounded')
                        ui.button('Delete', on_click=lambda e, _id=advert_id: delete_advert(_id)).classes('bg-red-500 text-white px-3 py-1 rounded')

def add_advert(title, description, price, category):
    collection.insert_one({
        'title': title,
        'description': description,
        'price': price,
        'category': category,
    })
    refresh_adverts()

def edit_advert(advert_id):
    advert = collection.find_one({"_id": ObjectId(advert_id)})
    if not advert:
        return
    with ui.dialog() as dialog, ui.card():
        ui.label('Edit Advert').classes('text-lg font-bold')
        title = ui.input('Title', value=advert['title'])
        description = ui.input('Description', value=advert['description'])
        price = ui.input('Price', value=advert['price'])
        category = ui.input('Category', value=advert['category'])
        with ui.row():
            ui.button(
                'Save',
                on_click=lambda: save_edit(advert_id, title.value, description.value, price.value, category.value, dialog)
            ).classes('bg-green-500 text-white')
            ui.button('Cancel', on_click=dialog.close).classes('bg-gray-400 text-white')
    dialog.open()

def save_edit(advert_id, title, description, price, category, dialog):
    collection.update_one(
        {"_id": ObjectId(advert_id)},
        {"$set": {
            'title': title,
            'description': description,
            'price': price,
            'category': category,
        }}
    )
    dialog.close()
    refresh_adverts()

def delete_advert(advert_id):
    collection.delete_one({"_id": ObjectId(advert_id)})
    refresh_adverts()

# ------------------- UI LAYOUT -------------------

ui.label('Advertisement Management Platform').classes(
    'text-3xl font-bold text-center mt-6 mb-6 text-indigo-700'
)

with ui.card().classes('max-w-lg mx-auto p-6 shadow-xl rounded-2xl mb-6'):
    ui.label('Post a New Advert').classes('text-xl font-semibold mb-4 text-gray-800')
    title = ui.input('Title').classes('w-full mb-2')
    description = ui.input('Description').classes('w-full mb-2')
    price = ui.input('Price').classes('w-full mb-2')
    category = ui.input('Category').classes('w-full mb-4')
    ui.button(
        'Post Advert',
        on_click=lambda: add_advert(title.value, description.value, price.value, category.value)
    ).classes('bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition')

advert_container = ui.column().classes('w-full px-6')

refresh_adverts()

ui.run()
