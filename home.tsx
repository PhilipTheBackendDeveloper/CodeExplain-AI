import React, { useEffect, useRef, useState } from 'react';
import { 
  StyleSheet, 
  View, 
  ScrollView, 
  Image, 
  TouchableOpacity, 
  Animated,
  Dimensions
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';

import { SvgXml } from 'react-native-svg';
import { Ionicons } from '@expo/vector-icons';
import { Text } from '@/components/ui/Text';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { theme } from '@/constants/theme';
import { s } from '@/utils/responsive';
import { WhereToBottomSheet } from '@/features/booking/components/WhereToBottomSheet';
import { Location } from '@/features/booking/booking.types';

const { width } = Dimensions.get('window');

const ELLIPSE_CARD_1 = `
<svg width="227" height="208" viewBox="0 0 227 208" fill="none" xmlns="http://www.w3.org/2000/svg">
<g filter="url(#filter0_f_615_1207)">
<circle cx="120" cy="88" r="50" fill="#ff9500ff"/>
</g>
<defs>
<filter id="filter0_f_615_1207" x="0" y="-32" width="240" height="240" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feFlood flood-opacity="0" result="BackgroundImageFix"/>
<feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
<feGaussianBlur stdDeviation="35" result="effect1_foregroundBlur_615_1207"/>
</filter>
</defs>
</svg>
`;

const ELLIPSE_CARD_2 = `
<svg width="254" height="221" viewBox="0 0 254 221" fill="none" xmlns="http://www.w3.org/2000/svg">
<g filter="url(#filter0_f_615_1208)">
<path d="M70 34.1711C70 46.2647 65.6168 57.9485 57.6624 67.0579C49.708 76.1674 149.483 155.541 137.5 157.171C125.517 158.801 23.5983 96.8252 13.5 90.1709C-28.1839 215.671 -24.9541 59.1787 -28.1839 47.5243C-31.4137 35.8699 -30.31 23.4399 -25.0773 12.5369C-19.8446 1.63397 -10.8375 -7.00296 0.27527 -11.7738C11.3881 -16.5447 23.8534 -17.1262 35.3621 -13.4105C46.8708 -9.69486 177.775 -22.1423 184 -11.7738L20 34.1711H70Z" fill="#F18F05"/>
</g>
<defs>
<filter id="filter0_f_615_1208" x="-100" y="-86" width="354" height="313.203" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feFlood flood-opacity="0" result="BackgroundImageFix"/>
<feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
<feGaussianBlur stdDeviation="35" result="effect1_foregroundBlur_615_1208"/>
</filter>
</defs>
</svg>
`;

const SERVICES = [
  { id: 'bus', name: 'Bus', image: require('../../assets/images/home/bus-home.png') },
  { id: 'minibus', name: 'Mini Bus', image: require('../../assets/images/home/mini-bus-home.png') },
  { id: 'cab', name: 'Cab', image: require('../../assets/images/home/cab-home.png') },
  { id: 'courier', name: 'Courier', image: require('../../assets/images/home/courier-home.gif') },
];

const MORE_WAYS = [
  { id: 'piktok', name: 'PikTok', image: require('../../assets/images/home/piktok-home.jpg') },
  { id: 'courier', name: 'Try Courier', image: require('../../assets/images/home/try-courier-home.jpg') },
  { id: 'rush', name: 'Rush', image: require('../../assets/images/home/rush-card-home.jpg') },
  { id: 'track', name: 'Live trip tracking', image: require('../../assets/images/home/live-track-home.jpg') },
];

function HomeScreen() {
  const router = useRouter();
  // Animation values
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  // Bottom Sheet State
  const [isWhereToVisible, setIsWhereToVisible] = useState(false);

  const handleLocationSelect = (location: Location, type: 'pickup' | 'dropoff') => {
    console.log('Selected:', type, location);
    // Handle location selection (e.g., navigate to next step)
  };

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
      <StatusBar style="dark" />
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }]
          }
        ]}>
          {/* Header */}
          <View style={styles.header}>
            <Text variant="title" style={styles.brandName}>WAYPIK</Text>
            <TouchableOpacity style={styles.iconButton}>
              <Ionicons name="map-outline" size={s(28)} color="#000" />
            </TouchableOpacity>
          </View>

          {/* Search Bar */}
          <View style={styles.searchSection}>
            <TouchableOpacity 
              style={styles.searchBar} 
              activeOpacity={0.9}
              onPress={() => setIsWhereToVisible(true)}
            >
              <Ionicons name="search" size={s(24)} color="#000" style={styles.searchIcon} />
              <Text style={styles.searchPlaceholder}>Where to?</Text>
              <View style={styles.verticalDivider} />
              <TouchableOpacity style={styles.rushDropdown}>
                <Image 
                  source={require('../../assets/images/home/rush-home.gif')} 
                  style={styles.rushGif} 
                  resizeMode="contain"
                />
                <Text style={styles.rushText}>Rush</Text>
                <Ionicons name="chevron-down" size={s(16)} color="#000" />
              </TouchableOpacity>
            </TouchableOpacity>
          </View>

          {/* Top Services */}
          <View style={styles.servicesRow}>
            {SERVICES.map((item) => (
              <TouchableOpacity key={item.id} style={styles.serviceItem}>
                <View style={styles.serviceIconContainer}>
                  <Image source={item.image} style={styles.serviceImage} resizeMode="contain" />
                </View>
                <Text style={styles.serviceName}>{item.name}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* More Ways section */}
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>More ways to WAYPIK</Text>
          </View>
          <View style={styles.moreWaysGrid}>
            {MORE_WAYS.map((item) => (
              <TouchableOpacity key={item.id} style={styles.moreWayItem}>
                <Image source={item.image} style={styles.moreWayImage} />
                <Text style={styles.moreWayName}>{item.name}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Suggested Trips Section */}
          <View style={styles.sectionHeader}>
            <Text variant="title" style={styles.suggestedTitle}>Suggested Trips</Text>
            <TouchableOpacity>
              <Text style={styles.seeAll}>See all</Text>
            </TouchableOpacity>
          </View>

          {/* Refined Ticket Card */}
          <View style={styles.ticketCardContainer}>
            {/* Liquid Glass Blobs with SVGs */}
            <View style={[styles.blob, styles.blob1]}>
              <SvgXml xml={ELLIPSE_CARD_2} width={s(254)} height={s(221)} />
            </View>
            <View style={[styles.blob, styles.blob2]}>
              <SvgXml xml={ELLIPSE_CARD_1} width={s(227)} height={s(208)} />
            </View>
            
            <View style={styles.ticketContent}>
              <View style={styles.ticketHeader}>
                <View style={styles.priceTagRefined}>
                  <Text style={styles.priceTextRefined}>₵130.00</Text>
                </View>
                
                {/* Seat Info (Rectangle 4188) */}
                <View style={styles.seatInfoRefined}>
                  <View style={styles.seatIconCircle}>
                    <Ionicons name="leaf" size={s(16)} color="#000" />
                  </View>
                  <Text style={styles.seatTextRefined}>0 of 40</Text>
                </View>
              </View>

              <View style={styles.routeContainerRefined}>
                <View style={styles.locationBlockRefined}>
                  <Text style={styles.timeTextRefined}>10:00 AM</Text>
                  <Text style={styles.cityCodeRefined}>KMS</Text>
                  <Text style={styles.cityNameRefined}>KUMASI</Text>
                </View>

                <View style={styles.pathContainerRefined}>
                  <View style={styles.pathLineRefined} />
                  <View style={styles.busIconWrapperRefined}>
                    <Ionicons name="bus" size={s(24)} color="#000" />
                  </View>
                  <View style={styles.pathLineRefined} />
                </View>

                <View style={styles.locationBlockRefined}>
                  <Text style={styles.timeTextRefined}>04:00PM</Text>
                  <Text style={styles.cityCodeRefined}>KMS</Text>
                  <Text style={styles.cityNameRefined}>KUMASI</Text>
                </View>
              </View>

              <TouchableOpacity
                style={styles.buyButtonFrame}
                activeOpacity={0.8}
                onPress={() => router.push('/(passenger)/booking/seat-selection')}
              >
                <Ionicons name="ticket" size={s(20)} color="#FFF" style={styles.ticketIconRotate} />
                <Text style={styles.buyButtonTextRefined}>BUY TICKET</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Animated.View>
      </ScrollView>

      <WhereToBottomSheet
        isVisible={isWhereToVisible}
        onClose={() => setIsWhereToVisible(false)}
        onLocationSelect={handleLocationSelect}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FBFAFA',
  },
  scrollContent: {
    paddingBottom: s(40),
  },
  content: {
    paddingHorizontal: s(20),
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: s(20),
    marginBottom: s(24),
  },
  brandName: {
    fontFamily: 'Lalezar_400Regular',
    fontSize: s(30),
    color: '#F59026',
    letterSpacing: 1,
    marginTop: s(20),
  },
  iconButton: {
    padding: s(4),
  },
  searchSection: {
    marginBottom: s(30),
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF1E0',
    borderRadius: s(30),
    paddingHorizontal: s(16),
    height: s(64),
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  searchIcon: {
    marginRight: s(12),
  },
  searchPlaceholder: {
    flex: 1,
    fontSize: s(18),
    fontFamily: 'Inter_600SemiBold',
    color: '#000',
  },
  verticalDivider: {
    width: 1,
    height: s(30),
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
    marginHorizontal: s(12),
  },
  rushDropdown: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    paddingHorizontal: s(12),
    paddingVertical: s(6),
    borderRadius: s(20),
    gap: s(4),
  },
  rushGif: {
    width: s(24),
    height: s(24),
  },
  rushText: {
    fontFamily: 'Inter_700Bold',
    fontSize: s(14),
    color: '#000',
  },
  servicesRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: s(32),
  },
  serviceItem: {
    alignItems: 'center',
    width: (width - s(40)) / 4.5,
  },
  serviceIconContainer: {
    width: s(64),
    height: s(64),
    backgroundColor: '#FFF',
    borderRadius: s(16),
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
    marginBottom: s(8),
  },
  serviceImage: {
    width: '80%',
    height: '80%',
  },
  serviceName: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: s(14),
    color: '#000',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: s(16),
  },
  sectionTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: s(14),
    color: '#000',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  moreWaysGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: s(32),
  },
  moreWayItem: {
    width: (width - s(52)) / 4,
    alignItems: 'center',
  },
  moreWayImage: {
    width: s(64),
    height: s(54),
    borderRadius: s(12),
    marginBottom: s(8),
  },
  moreWayName: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: s(12),
    color: '#000',
    textAlign: 'center',
  },
  suggestedTitle: {
    fontSize: s(24),
    fontFamily: 'Inter_700Bold',
    color: '#000',
  },
  seeAll: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: s(16),
    color: '#F59026',
  },
  ticketCardContainer: {
    backgroundColor: 'rgba(241, 143, 5, 0.2)',
    borderRadius: s(15),
    overflow: 'hidden',
    position: 'relative',
    width: '100%',
    height: s(221),
    marginBottom: s(16),
  },
  blob: {
    position: 'absolute',
  },
  blob1: {
    top: -s(40),
    left: -s(50),
    opacity: 0.8, 
  },
  blob2: {
    top: -s(16),
    left: s(170),
    opacity: 0.8,
  },
  ticketContent: {
    flex: 1,
    padding: 0,
  },
  ticketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: s(15),
    paddingTop: s(13),
  },
  priceTagRefined: {
    width: s(100),
    height: s(35),
    backgroundColor: 'rgba(241, 143, 5, 0.75)',
    borderRadius: s(14),
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: s(10),
  },
  priceTextRefined: {
    fontFamily: 'Inter_700Bold',
    fontSize: s(20),
    color: '#FFFFFF',
    marginLeft: s(4),
  },
  seatInfoRefined: {
    width: s(100),
    height: s(35),
    backgroundColor: 'rgba(241, 143, 5, 0.75)',
    borderRadius: s(14),
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: s(8),
    gap: s(6),
  },
  seatIconCircle: {
    width: s(30),
    height: s(30),
    borderRadius: s(15),
    backgroundColor: 'rgba(252, 246, 246, 0.58)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  seatTextRefined: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: s(14),
    color: '#FFFFFF',
  },
  routeContainerRefined: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: s(21),
    marginTop: s(17),
  },
  locationBlockRefined: {
    alignItems: 'flex-start',
  },
  timeTextRefined: {
    fontFamily: 'Inter_500Medium',
    fontSize: s(14),
    color: 'rgba(0, 0, 0, 0.5)',
    marginBottom: s(15),
  },
  cityCodeRefined: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: s(24),
    color: '#000000',
  },
  cityNameRefined: {
    fontFamily: 'Inter_500Medium',
    fontSize: s(18),
    color: 'rgba(0, 0, 0, 0.7)',
    marginTop: s(4), // Approximate positioning for 130px vs 99px top
  },
  pathContainerRefined: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: s(10), // Matching icon top 100px vs box flow
  },
  pathLineRefined: {
    width: s(57),
    height: 1,
    backgroundColor: '#000000',
  },
  busIconWrapperRefined: {
    marginHorizontal: s(12),
  },
  buyButtonFrame: {
    position: 'absolute',
    width: s(331),
    height: s(40),
    left: s(23),
    top: s(167),
    backgroundColor: '#F18F05',
    borderRadius: s(20),
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: s(10),
  },
  ticketIconRotate: {
    transform: [{ rotate: '-45deg' }],
  },
  buyButtonTextRefined: {
    fontFamily: 'Inter_700Bold',
    fontSize: s(16),
    color: '#FFFFFF',
  },
});

export default HomeScreen;
