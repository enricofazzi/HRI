(define (problem museum_problem)
    (:domain museum_guide)
    
    (:objects e0 e1 e2 l0 l1 l10 l11 l12 l13 l14 l15 l16 l17 l18 l19 l2 l3 l4 l5 l6 l7 l8 l9 pepper)
    (:init (at pepper l1) (connected e0 l0) (connected e1 l14) (connected e2 l8) (connected l0 e0) (connected l0 l1) (connected l0 l19) (connected l1 l0) (connected l1 l18) (connected l1 l2) (connected l10 l17) (connected l10 l9) (connected l12 l15) (connected l12 l5) (connected l14 e1) (connected l14 l15) (connected l15 l12) (connected l15 l14) (connected l15 l16) (connected l16 l15) (connected l16 l17) (connected l17 l10) (connected l17 l16) (connected l17 l18) (connected l17 l2) (connected l18 l1) (connected l18 l17) (connected l18 l19) (connected l19 l0) (connected l19 l18) (connected l2 l1) (connected l2 l17) (connected l2 l3) (connected l2 l9) (connected l3 l2) (connected l3 l4) (connected l4 l3) (connected l4 l5) (connected l5 l12) (connected l5 l4) (connected l7 l8) (connected l8 e2) (connected l8 l7) (connected l8 l9) (connected l9 l10) (connected l9 l2) (connected l9 l8) (entrance e0) (entrance e1) (entrance e2) (location l0) (location l1) (location l10) (location l11) (location l12) (location l13) (location l14) (location l15) (location l16) (location l17) (location l18) (location l19) (location l2) (location l3) (location l4) (location l5) (location l6) (location l7) (location l8) (location l9) (robot pepper))
    (:goal (or (at pepper e0) (at pepper e1) (at pepper e2)))
)