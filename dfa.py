if not change:
    obj.save()
    t_quantity = obj.quantity
    bom_details = BillOfMaterialDetails.objects.filter(bill_of_material=obj.bill_of_material)
    material_usage = []
    total_price = 0

    for i in bom_details:
        p = ProductUsage(item=i.material, manufacture=obj, quantity=(i.quantity * t_quantity),
                         price=(i.quantity * i.material.price), unit=i.unit)
        material_usage.append(p)
        total_price += p.price

    ProductUsage.objects.bulk_create(material_usage)
    obj.price = total_price
    obj.save()
else:
    product_usage = ProductUsage.objects.filter(manufacture=obj)
    total_price = 0
    for i in product_usage:
        if not i.price:
            price = i.quantity * i.item.price
            i.price = price
            i.save()
        total_price += i.price
    obj.price = total_price
    obj.save()