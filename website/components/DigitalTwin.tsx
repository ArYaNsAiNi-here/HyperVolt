'use client'

import { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, useGLTF } from '@react-three/drei'
import * as THREE from 'three'

interface DigitalTwinProps {
  lightIntensity: number // 0-100 from LDR sensor
  activeSource: 'solar' | 'battery' | 'grid'
  brightnessThreshold: number // 0-100 user preference
  weatherCondition?: string // 'sunny', 'cloudy', 'rainy', etc.
  className?: string
}

// House model component with GLTF support
function HouseModel({ 
  lightIntensity, 
  brightnessThreshold,
  weatherCondition = 'sunny' 
}: { 
  lightIntensity: number
  brightnessThreshold: number
  weatherCondition: string
}) {
  const houseRef = useRef<THREE.Group>(null)
  
  // Try to load GLTF model, fallback to basic house if not available
  let gltf: any = null
  try {
    gltf = useGLTF('/models/sus_room.glb')
  } catch (error) {
    console.log('GLTF model not found, using fallback')
  }

  // Calculate if artificial light is needed
  // Only show artificial lights if current sunlight doesn't meet user's brightness preference
  const needsArtificialLight = lightIntensity < brightnessThreshold
  const artificialLightIntensity = needsArtificialLight 
    ? ((brightnessThreshold - lightIntensity) / 100) * 1.5 
    : 0

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Gentle rotation for GLTF model
    if (houseRef.current && gltf) {
      houseRef.current.rotation.y = Math.sin(time * 0.2) * 0.05
    }
  })

  if (gltf) {
    // Render GLTF model
    return (
      <group ref={houseRef} position={[0, 0, 0]} scale={1}>
        <primitive object={gltf.scene} />
        
        {/* Indoor lighting - only when natural light is insufficient */}
        {needsArtificialLight && (
          <>
            <pointLight
              position={[0, 2, 0]}
              intensity={artificialLightIntensity}
              color="#FFE5B4"
              distance={6}
              decay={2}
            />
            <pointLight
              position={[-1, 1.5, 1]}
              intensity={artificialLightIntensity * 0.6}
              color="#FFE5B4"
              distance={4}
              decay={2}
            />
            <pointLight
              position={[1, 1.5, -1]}
              intensity={artificialLightIntensity * 0.6}
              color="#FFE5B4"
              distance={4}
              decay={2}
            />
          </>
        )}
      </group>
    )
  }

  // Fallback: Basic house model
  return (
    <group ref={houseRef} position={[0, 0, 0]}>
      {/* House base */}
      <mesh position={[0, 0.5, 0]}>
        <boxGeometry args={[2, 1, 2]} />
        <meshStandardMaterial 
          color="#2D3748"
        />
      </mesh>
      {/* Roof */}
      <mesh position={[0, 1.5, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[1.5, 1, 4]} />
        <meshStandardMaterial 
          color="#1F2937"
        />
      </mesh>
      {/* Indoor lights - only when natural light is insufficient */}
      {needsArtificialLight && (
        <>
          <pointLight
            position={[0, 1, 0]}
            intensity={artificialLightIntensity}
            color="#FFE5B4"
            distance={4}
            decay={2}
          />
          <pointLight
            position={[-0.5, 0.8, 0.5]}
            intensity={artificialLightIntensity * 0.6}
            color="#FFE5B4"
            distance={3}
            decay={2}
          />
        </>
      )}
    </group>
  )
}

// Visible sun mesh
function Sun({ 
  lightIntensity,
  weatherCondition 
}: { 
  lightIntensity: number
  weatherCondition: string
}) {
  const sunRef = useRef<THREE.Mesh>(null)
  const sunLightRef = useRef<THREE.DirectionalLight>(null)
  
  // Determine if it's daytime
  const isDaytime = lightIntensity > 20
  
  // Determine sunlight color and intensity based on weather
  const sunlightConfig = useMemo(() => {
    if (!isDaytime) {
      return { 
        color: '#1a1a2e', 
        intensity: 0.1,
        visible: false 
      }
    }

    // Daytime sunlight based on weather
    switch (weatherCondition.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return { 
          color: '#FFF4E0',
          intensity: Math.min(lightIntensity / 100 * 2, 1.8),
          visible: true
        }
      case 'cloudy':
      case 'overcast':
        return { 
          color: '#E8E8E8',
          intensity: Math.min(lightIntensity / 100 * 1.2, 1.0),
          visible: true
        }
      case 'rainy':
      case 'rain':
        return { 
          color: '#C0C0D0',
          intensity: Math.min(lightIntensity / 100 * 0.8, 0.6),
          visible: true
        }
      case 'foggy':
      case 'fog':
        return { 
          color: '#D0D0D8',
          intensity: Math.min(lightIntensity / 100 * 0.6, 0.5),
          visible: true
        }
      default:
        return { 
          color: '#FFF8DC',
          intensity: Math.min(lightIntensity / 100 * 1.5, 1.5),
          visible: true
        }
    }
  }, [lightIntensity, weatherCondition, isDaytime])

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Sun position based on time of day (LDR sensor)
    const sunAngle = (lightIntensity / 100) * Math.PI
    const sunX = Math.cos(sunAngle) * 8
    const sunY = Math.max(Math.sin(sunAngle) * 8, 1)
    const sunZ = Math.sin(sunAngle) * 3
    
    if (sunRef.current && isDaytime) {
      sunRef.current.position.set(sunX, sunY, sunZ)
      // Gentle pulsing
      const scale = 1 + Math.sin(time) * 0.05
      sunRef.current.scale.set(scale, scale, scale)
    }
    
    if (sunLightRef.current) {
      sunLightRef.current.position.set(sunX, sunY, sunZ)
      sunLightRef.current.intensity = sunlightConfig.intensity + Math.sin(time * 0.5) * 0.05
    }
  })

  return (
    <>
      {/* Visible sun sphere - only during daytime */}
      {sunlightConfig.visible && (
        <mesh ref={sunRef}>
          <sphereGeometry args={[0.5, 32, 32]} />
          <meshBasicMaterial 
            color={sunlightConfig.color}
          />
        </mesh>
      )}
      
      {/* Directional sunlight */}
      <directionalLight
        ref={sunLightRef}
        color={sunlightConfig.color}
        intensity={sunlightConfig.intensity}
        position={[3, 5, 2]}
        castShadow
      />
      
      {/* Ambient light for general scene visibility */}
      <ambientLight intensity={0.4} color={sunlightConfig.color} />
      
      {/* Hemisphere light for sky/ground color variation */}
      <hemisphereLight
        color={sunlightConfig.color}
        groundColor="#1a1a1a"
        intensity={sunlightConfig.intensity * 0.4}
      />
    </>
  )
}

function Scene({ 
  lightIntensity, 
  brightnessThreshold,
  weatherCondition = 'sunny'
}: { 
  lightIntensity: number
  brightnessThreshold: number
  weatherCondition?: string
}) {
  return (
    <>
      {/* House model (GLTF or fallback) */}
      <Suspense fallback={null}>
        <HouseModel 
          lightIntensity={lightIntensity}
          brightnessThreshold={brightnessThreshold}
          weatherCondition={weatherCondition}
        />
      </Suspense>

      {/* Weather-based sunlight with visible sun */}
      <Sun 
        lightIntensity={lightIntensity}
        weatherCondition={weatherCondition}
      />
    </>
  )
}

export default function DigitalTwin({ 
  lightIntensity, 
  activeSource, 
  brightnessThreshold,
  weatherCondition = 'sunny',
  className 
}: DigitalTwinProps) {
  return (
    <div className={className} style={{ width: '100%', height: '100%' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[5, 3, 5]} />
        <OrbitControls 
          enableZoom={true}
          enablePan={true}
          minDistance={2}
          maxDistance={20}
          autoRotate
          autoRotateSpeed={0.8}
        />
        <Scene 
          lightIntensity={lightIntensity} 
          brightnessThreshold={brightnessThreshold}
          weatherCondition={weatherCondition}
        />
      </Canvas>
    </div>
  )
}
