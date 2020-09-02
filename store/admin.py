from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review, Contact

class CategoryAdmin(admin.ModelAdmin):
	search_fields = ['name','description']
	prepopulated_fields = {"slug":("name",)}
	class Meta:
		model = Category

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
	date_hierarchy = 'created'
	list_display = ['name', 'price', 'stock', 'available', 'updated']
	search_fields = ['name','description']
	list_editable = ['price', 'available', 'stock']
	list_filter = ['price', 'available']
	readonly_fields = ['created', 'updated']
	prepopulated_fields = {"slug":("name",)}
	list_per_page = 20
	class Meta:
		model = Product

admin.site.register(Product, ProductAdmin)

class OrderItemAdmin(admin.TabularInline):
	model = OrderItem
	fieldsets = [
		('Product', {'fields': ['product',]}),
		('Quantity', {'fields': ['quantity',]}),
		('Price', {'fields': ['price',]}),
	]
	readonly_fields = ['product', 'quantity', 'price']
	can_delete = False
	max_num = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ['id', 'billingName', 'emailAddress', 'created']
	list_display_links = ['id', 'billingName']
	search_fields = ['id', 'billingName', 'emailAddress']
	readonly_fields = ['id', 'token', 'total', 'billingName','created', 'emailAddress',
					'billingAddress1','billingCity','billingPostcode','billingCountry','shippingName',
					'shippingAddress1','shippingCity','shippingPostcode','shippingCountry']
	fieldsets = [
		('ORDER INFORMATION', {'fields': ['id', 'token', 'total', 'created',]}),
		('BILLING INFORMATION', {'fields': ['billingName','billingAddress1',
						'billingCity','billingPostcode','billingCountry','emailAddress',]}),
		('SHIPPING INFORMATION', {'fields': ['shippingName','shippingAddress1','shippingCity',
						'shippingPostcode','shippingCountry',]}),		
	]

	inlines = [OrderItemAdmin,]

	def has_delete_permission(self, request, obj=None):
		return False

	def has_add_permission(self, request):
		return False

class ContactAdmin(admin.ModelAdmin):
	list_display = ['user', 'email', 'subject', 'created']
	readonly_fields = ['full_name','user','subject','email','content' ,'created']
	class Meta:
		model = Contact

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)
admin.site.register(Contact, ContactAdmin)