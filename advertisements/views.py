from django.db.models import Q
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement
from advertisements.permissions import IsOwnerOrReadOnly, IsNotOwner
from advertisements.serializers import AdvertisementSerializer
from rest_framework.decorators import action


class AdvertisementViewSet(ModelViewSet):

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = AdvertisementFilter

    def list(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            queryset = self.filter_queryset(Advertisement.objects.filter(Q(status='OPEN') | Q(status='CLOSED')).all())
        else:
            queryset = self.filter_queryset(Advertisement.objects.filter(Q(creator=request.user) | Q(status='OPEN') |
                                                                         Q(status='CLOSED')).all())
        serializer = AdvertisementSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=[IsAuthenticated, IsNotOwner])
    def favourite(self, request, pk):
        if request.method == 'POST':
            advertisement = self.get_object()
            request.user.favourite_advertisements.add(advertisement)
            return HttpResponse('Added to favourites.')
        elif request.method == 'DELETE':
            request.user.favourite_advertisements.remove(Advertisement.objects.get(id=pk))
            return HttpResponse('Removed from favourites.')

    @action(methods=['GET'], detail=False, url_path='favourites', permission_classes=[IsAuthenticated])
    def favourites(self, request):
        queryset = self.filter_queryset(request.user.favourite_advertisements.all())
        serializer = AdvertisementSerializer(queryset, many=True)
        return Response(serializer.data)
