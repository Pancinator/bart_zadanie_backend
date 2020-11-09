import datetime

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import GalerySerializerGet, GalerySerializerPostRead, GaleryDetailSerializerGet, \
    GalleryDetailSerializerPost
from .models import Galery, Image
from PIL import Image as I

@api_view(['GET'])  # function based decorator -> allows only usage of GET method
def api_overview(request):
    api_urls = {
        'List of galleries': 'api/gallery/',
        'List of images gallery': 'api/gallery/<name>',
    }
    return Response(api_urls)


@api_view(['GET', 'POST'])
def galleries(request):
    # GET request
    if request.method == 'GET':
        g = Galery.objects.all()
        serializer = GalerySerializerGet(g, many=True)
        return Response(serializer.data)

    # POST request
    elif request.method == 'POST':
        serializer = GalerySerializerPostRead(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            g = serializer.save()

            if g != 409:
                content = {
                    "name": g.name,
                    "path": g.path
                }
                return Response(content, status=status.HTTP_201_CREATED)
            else:
                return Response('Galéria so zadaným názvom už existuje', status=status.HTTP_409_CONFLICT)
        else:
            return Response('Chybne zadaný request - nevhodný obsah podľa schémy.', status=status.HTTP_400_BAD_REQUEST)


# Methods for working with galleries content
@api_view(['GET', 'POST', 'DELETE'])
def gallery_detail(request, gallery):
    # modify image info before saving, fill up additional fields
    def perform_create(ser, path, gallery, name, modified):
        return ser.save(fullpath=gallery + '/' + str(path), path=path, name=name, modified=modified)

    # GET request
    if request.method == 'GET':
        try:
            galleries = Galery.objects.get(name=gallery)
        except:
            return Response('Zvolená galéria neexistuje', status=status.HTTP_404_NOT_FOUND)

        serializer = GaleryDetailSerializerGet(galleries, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST request
    elif request.method == 'POST':
        serializer = GalleryDetailSerializerPost(data=request.data)

        if serializer.is_valid():
            name_of_picture = str(serializer.validated_data['image'])
            # check whether Image already exists
            try:
                Image.objects.get(fullpath=gallery + '/' + name_of_picture)
            except:
                modified = str(datetime.datetime.now())
                image = perform_create(serializer, serializer.validated_data['image'], gallery,
                                       name_of_picture.split('.')[0], modified)

                try:
                    g = Galery.objects.get(name=gallery)
                    g.images.add(image)
                except:
                    return Response('Galéria pre upload sa nenašla', status=status.HTTP_404_NOT_FOUND)
                # response JSON, it is possible to use another serializer too, but I go with this approach now
                response = {
                    "uploaded": {
                        "path": name_of_picture,
                        "fullpath": image.image.url,
                        "name": name_of_picture.split('.')[0],
                        "modified": modified
                    }
                }
                return Response(str(response), status=status.HTTP_201_CREATED)
            else:
                return Response('Obrázok už existuje', status=status.HTTP_409_CONFLICT)
        else:
            return Response('Nevalídny request', status=status.HTTP_400_BAD_REQUEST)

    # DELETE request
    elif request.method == 'DELETE':
        try:
            g = Galery.objects.get(name=gallery)
        except:
            return Response('Zvolená galéria/obrázok neexistuje', status=status.HTTP_404_NOT_FOUND)

        g.images.all().delete()
        Galery.objects.filter(name=gallery).delete()
        return Response('Galéria/obrázok bola úspešne vymazaná', status=status.HTTP_200_OK)


# Methods for handling DELETE request of the specific image in specific gallery
@api_view(['DELETE'])
def delete_image_from_galery(request, gallery, image):
    if request.method == 'DELETE':
        try:
            i = Image.objects.filter(fullpath=gallery + '/' + image)
            g = Galery.objects.get(name=gallery)
        except:
            return Response('Zvolená galéria/obrázok neexistuje', status=status.HTTP_404_NOT_FOUND)

        g.images.remove(i[0])
        i.delete()
        return Response('Galéria/obrázok bola úspešne vymazaná', status=status.HTTP_200_OK)


"""
image is basically fullpath field from Image instance. However there are no / symbols allowed while specifing
URL in browser so I have used _ symbols. After that _ symbols are replaced with / symbol to match the path.
"""
def calcualte_dimensions(w, h, i):
    if w == 0:
        s = i.size
        ratio = s[0] / s[1]
        w = round(h * ratio)
        return w, h
    elif h == 0:
        s = i.size
        ratio = s[0] / s[1]
        h = round(w * ratio)
        return w, h

@api_view(['GET'])
def generate_image_view(request, w, h, image):
    # GET request
    if request.method == 'GET':
        full_path = image.replace("_", "/")
        try:
            i = I.open(full_path)
        except:
            return Response('Obrázok sa nenašiel', status=status.HTTP_404_NOT_FOUND)

        if w == 0 or h == 0:
            w, h = calcualte_dimensions(w, h, i)
        i.thumbnail((w,h))
        return HttpResponse(i, content_type="image/jpeg", status=status.HTTP_200_OK)



