#/usr/bin/python3

import cv2,math,argparse
import matplotlib.pyplot as plt
from modules.twitter import twitter

# Variables globales de détection de yeux et de visages
eyeCascade = cv2.CascadeClassifier('./haarcascade/eye.xml')
faceCascade = cv2.CascadeClassifier('./haarcascade/frontalface_default.xml')
# Import global de LA moustache
mst = cv2.imread('./moustache.png')

def put_moustache(mst,fc,x,y,w,h,deg):

	# Tailles du visage
	face_width = w
	face_height = h

	# Calcul de la taille que prendra la moustache
	mst_width = int(face_width*0.4166666)+1
	mst_height = int(face_height*0.142857)+1
	# Taillage de moustache en conséquence
	mst = cv2.resize(mst,(mst_width,mst_height))
	# Rotation de la moustache en fonction de l'angle du visage !!NON OPÉRATIONNEL!!
	# if deg != None:
	# 	mst = cv2.rotate(mst, deg)

	# Alors là... Aucune idée du pourquoi du comment ça marche
	for i in range(int(0.62857142857*face_height),int(0.62857142857*face_height)+mst_height):
		for j in range(int(0.29166666666*face_width),int(0.29166666666*face_width)+mst_width):
			for k in range(3):
				if mst[i-int(0.62857142857*face_height)][j-int(0.29166666666*face_width)][k] <235:
					fc[y+i][x+j][k] = mst[i-int(0.62857142857*face_height)][j-int(0.29166666666*face_width)][k]

	return fc

def find_eyes(x,y,w,h,gray,SRC,debug):
	# Travaille sur le visage dans l'image en nuances de gris et en couleurs
	roi_gray = gray[y:y+h, x:x+w]
	roi_color = SRC[y:y+h, x:x+w]

	# Reconnaissance des yeux sur le visage
	eyes = eyeCascade.detectMultiScale(roi_gray,minNeighbors=20)

	if debug:
		print(f'\t{len(eyes)} {"yeux détectés" if len(eyes)>1 else "œil détecté"}' if len(eyes) != 0 else '\tPas d\'œil détecté')
		# Dessin d'un rectangle autour de chaque œil détecté
		for (ex,ey,ew,eh) in eyes:
			cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
	
	return eyes

def face_rotation(x,y,w,h,gray,SRC,debug):
	# Détection des yeux sur le visage
	eyes = find_eyes(x,y,w,h,gray,SRC,debug)

	# Si deux yeux sont détectés
	if len(eyes) == 2:
		# Définition de chaque œil
		leftEye = eyes[0]
		rightEye = eyes[1]
		# Calcule de l'angle entre chaque œil (cas où les yeux sont droits à l'horizontale)
		deg = int(math.degrees(math.atan((leftEye[1]-rightEye[1])/(leftEye[0]-rightEye[0]))))
		if debug:
			print(f'\tLe visage est tourné de {deg} degrés')
	else:
		return None

def main(source_image_path,debug):

	# Import des images sur lesquelles travailler 
	SRC = cv2.imread(source_image_path)			# Notre image source
	gray = cv2.cvtColor(SRC, cv2.COLOR_RGB2GRAY)# Notre image source en nuances de gris

	# Reconnaissance faciale stockée dans un tableau de coordonnées
	faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30, 30))
	print(f'{len(faces)} visage(s) trouvé(s) sur cette image\n')

	count = 1
	# Pour chaque visage, utilisation de ses coordonnées x,y et tailles w,h
	for (x,y,w,h) in faces:
		if debug:
			print(f'Visage {count} :')
			# Dessin du rectangle autour du visage détecté
			cv2.rectangle(SRC,(x,y),(x+w,y+h),(255,0,0),2)
			# Affichage du numéro du visage
			cv2.putText(SRC,str(count),(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0, 0, 255),2)
		# Définition de la rotation du visage
		deg = face_rotation(x,y,w,h,gray,SRC,debug)
		# Ajout de la moustache
		SRC = put_moustache(mst,SRC,x,y,w,h,deg)
		
		count += 1

	# Affichage de l'image une fois les opérations exécutées
	plt.axis('off')
	plt.imshow(cv2.cvtColor(SRC, cv2.COLOR_BGR2RGB))
	plt.show()

	# Sauvegarde de l'image sous le nom "./image.png"
	cv2.imwrite('./image.png',SRC)

	# Connexion au compte Twitter
	twitter.connect()
	# Publication de l'image
	twitter.postMedia('./image.png','test 1 test 2 testicucle')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='python script to add a mustache to people')
	parser.add_argument('-d', '--debug', help='draw rectangles and print stuffs to show how it works', action='store_true')
	parser.add_argument('-p', '--path', help='path to the source image (default is test.jpg)', default='./test.jpg')
	args = parser.parse_args()
	main(args.path,args.debug)