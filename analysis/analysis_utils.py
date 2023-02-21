import numpy as np
from sklearn.metrics import confusion_matrix

def unidirectional_score_ij(p_i2j, p_j2i, p_delta_positive, p_delta_negative, lags):
    """
    TODO: Add description. ONeNote for reference.
    """
    Score_x2y = (lags<0)*(1-p_delta_negative)*(1-p_j2i) + (lags>0)*(1-p_delta_positive)*(1-p_i2j)
    Score_y2x = (lags>0)*(1-p_delta_negative)*(1-p_j2i) + (lags<0)*(1-p_delta_positive)*(1-p_i2j)
    return Score_x2y, Score_y2x
    
def score_ij(p_i2j, p_j2i, p_delta):
    """
    TODO: Add description. ONeNote for reference.
    """
    return (1-p_i2j) * (1-p_j2i) * p_delta

def confusion_matrix_scores(GT_net, Pred_net, kwargs**):
    """
    TODO: Add description. ONeNote for reference.
    Only binary networks
    """
    # Flatten the networks to obtain performance
    GT_net_flat = list(np.int16(GT_net[np.triu_indices_from(GT_net, k=1)]))
    Pred_net_flat = list(np.int16(Pred_net[np.triu_indices_from(Pred_net, k=1)]))
    GT_net_flat.extend(np.int16(GT_net[np.tril_indices_from(GT_net, k=-1)]))
    Pred_net_flat.extend(np.int16(Pred_net[np.tril_indices_from(Pred_net, k=-1)]))

    # TODO: Constrain to 1st neighbours --> normalise with respect to the number of real/direct connections
    if kwargs["Mask_N1"]:
        pass
    elif kwargs["Mask_N2"]:
        pass
    else:
        pass
    
    tn, fp, fn, tp = confusion_matrix(GT_net_flat, Pred_net_flat).ravel() 
    # INFO: 
    # -----
    # tn => True negative
    # fp => False positive
    # fn => False negative
    # tp => True positive

    sensitivity = tp / (tp + fn) if (tp + fn)>0 else 0
    specificity = tn / (tn + fp) if (tn + fp)>0 else 0
    positive_predictive_value = tp / (tp + fp) if (tp + fp)>0 else 0

    return sensitivity, specificity, positive_predictive_value